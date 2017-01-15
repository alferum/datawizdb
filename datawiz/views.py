# -*- coding: utf-8 -*-
from django.shortcuts import render

from dwapi import datawiz
import pandas
import numpy
from datetime import datetime

date_from = '2015-11-17'
date_to = '2015-11-18'
categories = 72212

def home(request):
    dw = datawiz.DW('test1@mail.com', 'test2@cbe47a5c9466fe6df05f04264349f32b')

    info = dw.get_client_info()
    #info = {u'name': u'test2', u'date_from': datetime(2014, 5, 1, 1, 2, 7), u'root_category': 73557, u'date_to': datetime(2015, 11, 18, 22, 0), u'timezone': 3,
    #        u'shops': {641: u'Shop \u211601', 3403: u'Bizare', 595: u'Shop \u211602', 3404: u'Bizare2', 601: u'Shop \u211603'}}
    
    data = dw.get_categories_sale(date_from=date_from, date_to=date_to, categories = [72495, "sum"], by=["turnover", "qty", "receipts_qty"], view_type="raw")
    data = data.reindex(index=[2, 3], columns=['date', 'turnover', 'qty', 'receipts_qty'])
    #data = pandas.DataFrame({'date': [date_from, date_to], 'turnover': [48707.43, 19823.23], 'qty': [4147.958, 1775.816], 'receipts_qty': [1976, 917]})
    data['mean'] = data['turnover'] / data['receipts_qty']
    data = data.pivot_table(columns=['date'], values=['turnover', 'qty', 'receipts_qty', 'mean'])
    data['diff'] = data[date_to] - data[date_from]
    data['percent'] = data['diff'] * 100 / data[date_from]
    data = numpy.round(data, 2)
    data = data.reindex(index=['turnover', 'qty','receipts_qty', 'mean'], columns=[date_to, date_from, 'percent', 'diff'])
    data.columns.name = 'Показник'
    data.rename({'turnover': 'Оборот', 'qty': 'Кількість товарів', 'receipts_qty': 'Кількість чеків', 'mean': 'Середній чек'},
                columns={date_to: datetime.strptime(date_to, '%Y-%m-%d').strftime('%d-%m-%Y'),
                         date_from: datetime.strptime(date_from, '%Y-%m-%d').strftime('%d-%m-%Y'), 'percent': 'Різниця в %', 'diff': 'Різниця'}, inplace=True)

    sale = dw.get_products_sale(date_from=date_from, date_to=date_to, categories=categories, by=['turnover', 'qty'], view_type='raw')
    sale = sale.pivot_table(index='name', columns=['date'], values=['turnover', 'qty'], fill_value=0)
    sale['diff_qty'] = sale['qty', date_to] - sale['qty', date_from]
    sale['diff_turnover'] = sale['turnover', date_to] - sale['turnover', date_from]
    del sale['turnover'], sale['qty']
    sale.index.name = None
    sale.columns = sale.columns.droplevel(level=1)
    sale.columns.name = 'Назва товару'
    sale = sale.rename(columns={'diff_qty': 'Зміна кількості продаж', 'diff_turnover': 'Зміна обороту'})
    sale_up = sale[sale['Зміна обороту']>0]
    sale_down = sale[sale['Зміна обороту']<0]
    
    return render(request, 'datawiz/home.html', {'info': info, 'data': data.to_html(), 'sale_up': sale_up.to_html(), 'sale_down': sale_down.to_html()})
