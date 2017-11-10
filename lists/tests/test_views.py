# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.urls import resolve
from lists.views import home_page
from django.http import HttpRequest
from lists.models import Item, List

class HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = home_page(request)
        html = str(response.content).encode("utf-8").replace('\n', '')
        self.assertTrue(html.startswith('<html>'))
        self.assertIn("<title>To-Do lists</title>".encode("utf-8"), html)
        self.assertTrue(html.strip().endswith('</html>'))

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_only_saves_items_when_is_necessary(self):
        self.client.get('/')
        self.assertEqual(Item.objects.count(), 0)

class ListViewTest(TestCase):

    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get('/lists/' + str(correct_list.id) + '/')
        self.assertEqual(response.context['list'], correct_list)

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get('/lists/'+str(list_.id)+'/')
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_all_items(self):
        correct_list = List.objects.create()
        Item.objects.create(text='itemey 1', list=correct_list)
        Item.objects.create(text='itemey 2', list=correct_list)
        other_list = List.objects.create()
        Item.objects.create(text='other list item 1', list= other_list)
        Item.objects.create(text='other list item 2', list= other_list)

        response = self.client.get('/lists/'+str(correct_list.id)+'/')

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
        self.assertNotContains(response, 'other list item 1')
        self.assertNotContains(response, 'other list item 2')

    def test_validation_errors_are_sent_back_to_home_page_template(self):
        response = self.client.post('/lists/new', data= {'item_text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        expected_error = escape("You can't have an empty list item")
        print(response.conten.decode())
        self.asserContains(response, expected_error)

    def test_invalid_list_items_arent_saved(self):
        self.client.post('/lists/new', data = {'item_text': ''})
        self.asserEqual(List.objects.count(), 0)
        self.asserEqual(Item.objects.count(), 0)

    def test_can_save_a_POST_request(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            '/lists/'+str(correct_list.id)+'/',
            data={'item_text': 'A new item for an existing list'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_redirect_after_POST(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()


        response = self.client.post(
            '/lists/' + str(correct_list.id) + '/add_item',
            data={'item_text': 'A new item for an existing list'})

        self.assertRedirects(response, '/lists/'+str(correct_list.id)+'/')

    def test_POST_redirects_to_live_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        self.client.post(
            '/lists/'+str(correct_list.id)+'/',
            data={'item_text': 'A new item for an existing list'}
        )
        self.assertRedirects(response, '/lists/'+str(correct_list.id)+'/')
