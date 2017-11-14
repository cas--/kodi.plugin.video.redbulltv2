# from enum import Enum
import re, urllib2, pprint
import utils

class ElementType: #(Enum):
    collection = 1
    product = 2

class RedbullTVClient(object):
    REDBULL_STREAMS = "https://dms.redbull.tv/v3/"
    REDBULL_API = "https://api.redbull.tv/v3/"
    ROOT_MENU = [
        {"title": "Discover", "url": REDBULL_API + "products/discover", "is_content":False},
        {"title": "TV", "url": REDBULL_API + "products/schedule", "is_content":False},
        {"title": "Channels", "url": REDBULL_API + "products/channels", "is_content":False},
        {"title": "Calendar", "url": REDBULL_API + "products/calendar", "is_content":False},
        {"title": "Search", "url": REDBULL_API + "search?q=", "is_content":False},
    ]

    token = None

    def __init__(self, resolution=None):
        self.resolution = resolution

    @staticmethod
    def get_resolution_code(video_resolution_id):
        return {
            "0" : "320x180",
            "1" : "426x240",
            "2" : "640x360",
            "3" : "960x540",
            "4" : "1280x720",
        }.get(video_resolution_id, "1920x1080")

    def get_stream_url(self, streams_url):
        url = streams_url
        try:
            playlists = urllib2.urlopen(url).read()
            resolution = self.get_resolution_code(self.resolution)
            media_url = re.search(
                "RESOLUTION=" + resolution + ".*\n(.*)",
                playlists).group(1)
        except Exception:
            pass
        else:
            url = media_url

        # Should use specific resolution stream, if that failed will use the 
        # playlist url passed in and kodi will choose a stream
        return url

    def get_image_url(self, id, resources, width=500, quality=70):
        url = "https://resources.redbull.tv/" + id + "/"

        if "rbtv_cover_art_landscape" in resources:
            url += "rbtv_cover_art_landscape/im"
        elif "rbtv_display_art_landscape" in resources:
            url += "rbtv_display_art_landscape/im"
        elif "rbtv_background_landscape" in resources:
            url += "rbtv_background_landscape/im"

        if width:
            url += ":i:w_500"

        if quality:
            url += ",q_70"
        
        return url

    def get_element_details(self, element, element_type, parent_image_url = None):
        details = {"is_content":False, "image": parent_image_url}
        # details["is_content"] = element.get("playable")# == "video"
        if element.get("playable") or element.get("action") == "play":
            details["is_content"] = True
            details["url"] = self.REDBULL_STREAMS + element["id"] + "/" + self.token + "/playlist.m3u8"
            if element.get("duration"):
                details["duration"] = element.get("duration") / 1000
        elif element.get("start_time") and element.get("label") == "Upcoming": # and element.get("status").get("start_time"):
            details["event_date"] = element["start_time"]
        elif element_type == ElementType.collection:
            details["url"] = self.REDBULL_API + "collections/" + element["id"] # + "?limit=20"
        elif element_type == ElementType.product:
            details["url"] = self.REDBULL_API + "products/" + element["id"] #+"?limit=20"
        subtitle = element.get("subheading")

        details["title"] = (element.get("label") or element.get("title")) + ((" - " + subtitle) if subtitle else "")
        details["summary"] = element.get("long_description")
        if element.get("resources"):
            # Check for resource, possibly have a look for resources based on preferences. Handle res accordingly
            details["image"] =  self.get_image_url(element.get("id"), element.get("resources"))
        # details["event_date"] = element.findtext('.//rightLabel')

        # Strip out any keys with empty values
        return {k:v for k, v in details.iteritems() if v is not None}

    def get_items(self, url=None, page=1, limit=20):       
        # If no url is specified, return the root menu
        if url is None:
            return self.ROOT_MENU

        pprint.pprint("pprint: in get_items: "+ url)
        # print("print: in get_items")

        # pprint.pprint(session_response)
        if self.token is None:
            pprint.pprint('Setting token');
            session_response = utils.get_json("https://api.redbull.tv/v3/session?category=smart_tv&os_family=android")
            self.token = session_response["token"]

        # pprint.pprint(self.NEW_ROOT_MENU[0]["url"])
        # result = utils.get_json(self.NEW_ROOT_MENU[0]["url"]+"", token)
        # pprint.pprint(url+"?limit="+str(limit)+"&offset="+str((page-1)*limit),)
        result = utils.get_json(url+"?limit="+str(limit)+"&offset="+str((page-1)*limit), self.token)
        # pprint.pprint(result)

        image_url = self.get_image_url(result.get("id"), result.get("resources")) if result.get("resources") else None

        items = []
        if 'status' in result:
            items.append(self.get_element_details(result["status"], ElementType.product, image_url))
        if 'links' in result:
            links = result["links"]
            for link in links:
                items.append(self.get_element_details(link, ElementType.product, image_url))

        if 'collections' in result:
            collections = result["collections"]

            # Handle Search results
            if collections[0].get("collection_type") == "top_results":
                result["items"] = collections[0]["items"]
            else:            
                for collection in collections:
                    items.append(self.get_element_details(collection, ElementType.collection))
        
        if 'items' in result:
            result_items = result["items"]
            for result_item in result_items:
                items.append(self.get_element_details(result_item, ElementType.product, image_url))

        # Add next item if meta.total > meta.offset + meta.limit

        # pprint.pprint(items)
        # print(items)
        # print("client result count: "+str(len(items)))

        return items
