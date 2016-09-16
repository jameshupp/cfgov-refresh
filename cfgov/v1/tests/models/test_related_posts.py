import mock

from unittest import TestCase
from v1.models.base import CFGOVPage, CFGOVPageCategory
from v1.models.learn_page import AbstractFilterPage

from v1.tests.wagtail_pages import helpers

import datetime as dt


class RelatedPostsTestCase(TestCase):

    def setUp(self):

        self.hostname = 'localhost'

        # add some authors to a CFGOV page and give it some tags

        self.author1 = 'Some Author'
        self.author2 = 'Another Person'
        self.author3 = 'A Third Author'
        self.page_with_authors = CFGOVPage(title='a cfgov page with authors')
        helpers.save_new_page(self.page_with_authors)

        self.page_with_authors.authors.add(self.author1)
        self.page_with_authors.authors.add(self.author2)
        self.page_with_authors.authors.add(self.author3)

        self.page_with_authors.tags.add('tag 1')
        self.page_with_authors.tags.add('tag 2')

        # set up parent pages for the different types of related
        # posts we can have

        self.blog_parent = CFGOVPage(slug='blog', title='blog parent')
        self.newsroom_parent = CFGOVPage(slug='newsroom', title='newsroom parent')
        self.events_parent = CFGOVPage(slug='events', title='events parent')
        self.archive_events_parent = CFGOVPage(slug='archive-past-events', title='archive past events parent')

        helpers.save_new_page(self.blog_parent)
        helpers.save_new_page(self.newsroom_parent)
        helpers.save_new_page(self.events_parent)
        helpers.save_new_page(self.archive_events_parent)

        # set up children of the parent pages and give them some tags
        # and some categories

        self.blog_child1 = AbstractFilterPage(title='blog child 1', date_published=dt.date(2016, 9, 1))
        self.blog_child1.tags.add('tag 1')
        self.blog_child1.categories.add(CFGOVPageCategory(name='info-for-consumers'))

        self.blog_child2 = AbstractFilterPage(title='blog child 2', date_published=dt.date(2016, 9, 2))
        self.blog_child2.tags.add('tag 2')
        self.blog_child2.categories.add(CFGOVPageCategory(name='policy_compliance'))

        self.newsroom_child1 = AbstractFilterPage(title='newsroom child 1', date_published=dt.date(2016, 9, 2))
        self.newsroom_child1.tags.add('tag 1')
        self.newsroom_child1.tags.add('tag 2')
        self.newsroom_child1.categories.add(CFGOVPageCategory(name='op-ed'))

        self.newsroom_child2 = AbstractFilterPage(title='newsroom child 2', date_published=dt.date(2016, 9, 3))
        self.newsroom_child2.tags.add('tag 2')
        self.newsroom_child2.categories.add(CFGOVPageCategory(name='some-other-category'))

        self.events_child1 = AbstractFilterPage(title='events child 1', date_published=dt.date(2016, 9, 7))
        self.events_child1.tags.add('tag 1')

        self.events_child2 = AbstractFilterPage(title='events child 2', date_published=dt.date(2016, 9, 5))
        self.events_child2.tags.add('tag 2')

        helpers.save_new_page(self.blog_child1, self.blog_parent)
        helpers.save_new_page(self.blog_child2, self.blog_parent)
        helpers.save_new_page(self.newsroom_child1, self.newsroom_parent)
        helpers.save_new_page(self.newsroom_child2, self.newsroom_parent)
        helpers.save_new_page(self.events_child1, self.events_parent)

        # mock a stream block that dictates how to retrieve the related posts
        # note that because of the way that the related_posts_category_lookup function
        # works i.e. by consulting a hard-coded object, the specific_categories
        # slot of the dict has to be something that it can actually find.

        self.block = mock.MagicMock()
        self.block.block_type = 'related_posts'
        self.block.value = dict({
            'limit': 3,
            'show_heading': True,
            'header_title': 'Further reading',
            'relate_posts': False,
            'relate_newsroom': False,
            'relate_events': False,
            'specific_categories': []
        })

    def tearDown(self):

        # you don't need to delete the children independently,
        # you can just delete the parent and it cascades

        self.blog_parent.delete()
        self.newsroom_parent.delete()
        self.events_parent.delete()
        self.archive_events_parent.delete()

        self.page_with_authors.delete()

    def test_related_posts_blog(self):

        self.block.value['relate_posts'] = True
        self.block.value['relate_newsroom'] = False
        self.block.value['relate_events'] = False
        self.block.value['specific_categories'] = ['Info for Consumers', 'Policy &amp; Compliance']

        related_posts = self.page_with_authors.related_posts(self.block, self.hostname)

        self.assertIn('Blog', related_posts)
        self.assertEqual(len(related_posts['Blog']), 2)
        self.assertEqual(related_posts['Blog'][0], self.blog_child2)
        self.assertEqual(related_posts['Blog'][1], self.blog_child1)
        self.assertNotIn('Newsroom', related_posts)
        self.assertNotIn('Events', related_posts)

    def test_related_posts_blog_limit(self):

        self.block.value['relate_posts'] = True
        self.block.value['relate_newsroom'] = False
        self.block.value['relate_events'] = False
        self.block.value['limit'] = 1
        self.block.value['specific_categories'] = ['Info for Consumers', 'Policy &amp; Compliance']

        related_posts = self.page_with_authors.related_posts(self.block, self.hostname)

        self.assertIn('Blog', related_posts)
        self.assertEqual(len(related_posts['Blog']), 1)
        self.assertEqual(related_posts['Blog'][0], self.blog_child2)
        self.assertNotIn('Newsroom', related_posts)
        self.assertNotIn('Events', related_posts)

    def test_related_posts_newsroom(self):

        self.block.value['relate_posts'] = False
        self.block.value['relate_newsroom'] = True
        self.block.value['relate_events'] = False
        self.block.value['specific_categories'] = ['Op-Ed']

        related_posts = self.page_with_authors.related_posts(self.block, self.hostname)

        self.assertIn('Newsroom', related_posts)
        self.assertEqual(len(related_posts['Newsroom']), 1)
        self.assertEqual(related_posts['Newsroom'][0], self.newsroom_child1)
        self.assertNotIn('Blog', related_posts)
        self.assertNotIn('Events', related_posts)

    def test_related_posts_events(self):

        self.block.value['relate_posts'] = False
        self.block.value['relate_newsroom'] = False
        self.block.value['relate_events'] = True
        self.block.value['specific_categories'] = ['anything', 'can', 'be', 'here']

        related_posts = self.page_with_authors.related_posts(self.block, self.hostname)

        self.assertIn('Events', related_posts)
        self.assertEqual(len(related_posts), 1)
        self.assertEqual(related_posts['Events'][0], self.events_child1)
        self.assertNotIn('Blog', related_posts)
        self.assertNotIn('Newsroom', related_posts)

    def test_related_posts_events_archive(self):

        helpers.save_new_page(self.events_child2, self.archive_events_parent)

        self.block.value['relate_posts'] = False
        self.block.value['relate_newsroom'] = False
        self.block.value['relate_events'] = True
        self.block.value['specific_categories'] = ['anything', 'can', 'be', 'here']

        related_posts = self.page_with_authors.related_posts(self.block, self.hostname)

        self.assertIn('Events', related_posts)
        self.assertEqual(len(related_posts['Events']), 2)
        self.assertNotIn('Blog', related_posts)
        self.assertNotIn('Newsroom', related_posts)
        self.assertEqual(related_posts['Events'][0], self.events_child1)
        self.assertEqual(related_posts['Events'][1], self.events_child2)

    def test_related_posts_all(self):

        self.block.value['relate_posts'] = True
        self.block.value['relate_newsroom'] = True
        self.block.value['relate_events'] = True
        self.block.value['specific_categories'] = ['Info for Consumers',
                                                   'Policy &amp; Compliance',
                                                   'Op-Ed']

        related_posts = self.page_with_authors.related_posts(self.block, self.hostname)

        self.assertIn('Blog', related_posts)
        self.assertIn('Newsroom', related_posts)
        self.assertIn('Events', related_posts)

        self.assertEqual(len(related_posts['Blog']), 2)
        self.assertEqual(len(related_posts['Events']), 1)
        self.assertEqual(len(related_posts['Newsroom']), 1)

        self.assertEqual(related_posts['Blog'][0], self.blog_child2)
        self.assertEqual(related_posts['Blog'][1], self.blog_child1)
        self.assertEqual(related_posts['Events'][0], self.events_child1)
        self.assertEqual(related_posts['Newsroom'][0], self.newsroom_child1)



