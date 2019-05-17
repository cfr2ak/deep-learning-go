import os
import sys
import multiprocessing
import six
from urllib.request import urlopen, urlretrieve


def worker(url_and_target):
    try:
        (url, target_path) = url_and_target
        print('>>> Downloading ' + target_path)
        urlretrieve(url, target_path)
    except (KeyboardInterrupt, SystemExit):
        print('>>> Exiting child process')


class KGSIndex:
    def __init__(
            self,
            kgs_url='https://u-go.net/gamerecords/',
            index_page='kgs_index.html',
            data_directory='data'):
        self.kgs_url = kgs_url
        self.index_page = index_page
        self.data_directory = data_directory
        self.file_infos = []
        self.urls = []
        self.load_index()

    def _download_zip_files(self):
        if not os.path.isdir(self.data_directory):
            os.makedirs(self.data_directory)
        urls_to_download = self._get_urls_to_download()
        cores = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(processes=cores)
        self._parallel_download(pool, urls_to_download)

    @staticmethod
    def _parallel_download(pool, urls_to_download):
        try:
            it = pool.imap(worker, urls_to_download)
            for _ in it:
                pass
            pool.close()
            pool.join()
        except KeyboardInterrupt:
            print('>>> Caught KeyboardInterrupt, terminating workers')
            pool.terminate()
            pool.join()
            sys.exit(-1)

    def _get_urls_to_download(self):
        urls_to_download = []
        for file_info in self.file_infos:
            url = file_info['url']
            file_name = file_info['filename']
            if not os.path.isfile(self.data_directory + '/' + file_name):
                urls_to_download.append((url, self.data_directory + '/' + file_name))
        return urls_to_download

    def _create_index_page_not_exist(self):
        if os.path.isfile(self.index_page):
            print('>>> Reading cached index page')
            index_file = open(self.index_page, 'r')
            index_contents = index_file.read()
            index_file.close()
        else:
            print('>>> Downloading index page')
            fp = urlopen(self.kgs_url)
            data = six.text_type(fp.read())
            fp.close()
            index_contents = data
            index_file = open(self.index_page, 'w')
            index_file.write(index_contents)
            index_file.close()
        return index_contents








