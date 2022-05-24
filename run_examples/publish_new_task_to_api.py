import requests

if __name__ == "__main__":
    url = 'http://0.0.0.0:8080/api/loader_task/'
    data = dict(
        method='get_page_content_after_click_sequence',
        url='https://www.lockaway-storage.com/',
        waiting_xpath='//div[@class="storage-container"]'
                      '//a[contains(@href, "storage-units")]/@href',
        click_xpath_list=[[
            '//div[contains(@class, "menu-item")]//a[contains(text(), "Storage Locations")]/..',
            '//div[contains(@class, "facilities-container")]'
            '//a[contains(@href, "storage-units")]/@href'
        ]]
    )
    resp = requests.post(url, json=data)
    print(resp.status_code)
