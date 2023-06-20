import os
from requests import get
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor

API_BASE_URL: str = 'https://api.mangadex.org/at-home/server/'
API_PARAM: str = '?forcePort443=false'

global img_progress
global total_images


def download_image(url: str, save_directory: str, progress_bar):
    global img_progress
    progress_bar.update_img_progress(img_progress / total_images * 100)
    progress_bar.display()

    response = get(url)
    if response.status_code == 200:
        filename = url.split("/")[-1]
        save_path = os.path.join(save_directory, filename)
        with open(save_path, 'wb') as file:
            file.write(response.content)
    img_progress += 1


def download_images_from_api(chap_hashes: list, progress_bar, save_directory: str):
    chap_progress = 1
    global img_progress
    img_progress = 1

    for chap in chap_hashes:

        progress_bar.update_chap_progress(chap_progress / len(chap_hashes) * 100)
        progress_bar.display()

        if not os.path.exists(f"{save_directory}/{chap[1]}"):
            # Create the new folder
            os.makedirs(f"{save_directory}/{chap[1]}")

        response = get(API_BASE_URL + chap[0] + API_PARAM)
        if response.status_code == 200:
            data = response.json()
            base_url = data['baseUrl']
            image_hashes = data['chapter']['hash']
            image_data = data['chapter']['data']

            global total_images
            total_images = len(image_data)

            with ThreadPoolExecutor(max_workers=4) as executor:
                download_tasks = []
                for image_name in image_data:
                    image_url = f"{base_url}/data/{image_hashes}/{image_name}"
                    task = executor.submit(download_image, image_url, f"{save_directory}/{chap[1]}", progress_bar)
                    download_tasks.append(task)

                for task in as_completed(download_tasks):
                    task.result()
            # for image_name in image_data:
            #     progress_bar.update_img_progress(img_progress / len(image_data) * 100)
            #     progress_bar.display()
            #     image_url = f"{base_url}/data/{image_hashes}/{image_name}"
            #     download_image(image_url, save_directory)
            #     img_progress += 1
        else:
            print(f"Failed to retrieve API response from URL: {response.status_code}")
        chap_progress += 1
        img_progress = 1
