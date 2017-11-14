#!/usr/bin/env python
import sys, os, pprint, json, time
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import lib.redbulltv_client as redbulltv

class ITTestRedbulltvClient(unittest.TestCase):
    redbulltv_client = redbulltv.RedbullTVClient('4')

    def test_get_root_menu(self):
        test_data = [
            (
                None,
                [
                    {'url': 'https://api.redbull.tv/v3/products/discover', 'is_content': False, 'title': 'Discover'},
                    {'url': 'https://api.redbull.tv/v3/products/schedule', 'is_content': False, 'title': 'TV'},
                    {'url': 'https://api.redbull.tv/v3/products/channels', 'is_content': False, 'title': 'Channels'},
                    {'url': 'https://api.redbull.tv/v3/products/calendar', 'is_content': False, 'title': 'Calendar'},
                    {'url': 'https://api.redbull.tv/v3/search?q=', 'is_content': False, 'title': 'Search'}
                ]
            ),
        ]
        for inp, expected in test_data:
            self.assertEqual(self.redbulltv_client.get_items(inp), expected)

    def test_get_discover_categories(self):
        """
        List the categorires from the Discover Page
        Check for more than 5 categories and explicitly check the first 2
        """
        test_data = 'https://api.redbull.tv/v3/products/discover'

        result = self.redbulltv_client.get_items(test_data)

        self.assertGreater(len(result), 5)
        self.assertEqual(result[0].get("title"), "Featured")
                
        # # TODO Order changed, Rather loop through an make sure Featured & Daily Highlights are in the list
        # self.assertEqual(result[1].get("category"), "Daily Highlights")

    def test_get_category_items(self):
        """
        List the items for a specific category on the Discover Page
        Check for more than 5 items in the 'Featured' & 'Daily Highlights' categories
        """
        test_data = [
            ('https://api.redbull.tv/v3//collections/playlists::8492e568-626a-48a3-b0d7-6d11e0f00dc3'),
            ('https://api.redbull.tv/v3//collections/playlists::3f81040a-2f31-4832-8e2e-545b1d39d173'),
        ]

        for inp in test_data:
            result = self.redbulltv_client.get_items(inp)
            # pprint.pprint(json.dumps(result))
            self.assertGreater(len(result), 5)

    def test_watch_now_stream(self):
        """
        Test the Watch Now Live Stream and confirm a resolution specific playlist is returned
        """
        test_data = (
            ('https://dms.redbull.tv/v3/linear-borb/_v3/playlist.m3u8'),
            [
                'https://dms.redbull.tv/v3/linear-borb/_v3/playlist.m3u8'
            ]
        )
        inp, expected = test_data
        result = self.redbulltv_client.get_stream_url(inp)
        pprint.pprint(result)
        self.assertNotEqual(result, expected[0])

    def test_search(self):
        """
        Test the Search functionality
        """
        test_data = ('https://api.redbull.tv/v3/search?q=drop')
        result = self.redbulltv_client.get_items(test_data)
        # pprint.pprint(json.dumps(result))
        self.assertGreater(len(result), 0)
    
    def test_upcoming_live_event(self):
        """
        Test upcoming live events
        """
        # test_data = ('https://appletv.redbull.tv/products/AP-1RCTZ2TMD2111?show_schedule=true%27);%22%20onPlay=%22loadPage(%27https://appletv.redbull.tv/products/AP-1RCTZ2TMD2111?show_schedule=true', None)
        result = self.redbulltv_client.get_items("https://api.redbull.tv/v3/products/calendar")
        pprint.pprint(result)
        # pprint.pprint(result[1]["url"]);
        # TODO: Don't rely on order
        result = self.redbulltv_client.get_items(result[1]["url"]) # Get Upcoming Live Events
        pprint.pprint(result)
        # result = self.redbulltv_client.get_items((item for item in result if item["title"] == "Schedule").next()["url"])
        # result = self.redbulltv_client.get_items([item for item in result if item["title"] == "Schedule"][0]["url"])
        result = self.redbulltv_client.get_items(result[1]["url"])
        # result = self.redbulltv_client.get_items(filter(lambda item: item['title'] == 'Schedule', result)[0]["url"])
        pprint.pprint(result)
        # result = self.redbulltv_client.get_items([item for item in result if item["title"] == "Upcoming"][0]["url"])
        # pprint.pprint(result)
        self.assertIn('event_date', result[0])
        self.assertGreater(result[0]["event_date"], time.time())

if __name__ == '__main__':
    unittest.main()
