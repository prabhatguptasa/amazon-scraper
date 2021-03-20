# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exporters import CsvItemExporter


class AmazonPipeline:

    def __init__(self):
        self.file = {}

    def open_spider(self, spider):
        file_name = f"dbs/{spider.name}.csv"
        self.file = open(file_name, 'wb')
        self.exporter = CsvItemExporter(self.file)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):

        main_data = item['row']
        item = main_data[0]
        self.exporter.export_item(item)
        return item
