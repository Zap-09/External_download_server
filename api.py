import os
import aiohttp
import asyncio
import zipfile as zf
import shutil
import re

save_folder = "Downloads"

os.makedirs(save_folder,exist_ok=True)

async def download(session, url,filename):

    async with session.get(url) as response:
        if response.status == 200:
            content = await response.read()

            with open(f"{filename}","wb") as f:
                f.write(content)
        else:
            print(f"Failed to download {url} - Status code {response.status}")


async def download_asyncly(urls,folder_name):

    async with aiohttp.ClientSession() as session:

        os.makedirs(os.path.join(save_folder,folder_name),exist_ok=True)
        tasks = []

        for index, url in enumerate(urls,start=1):
            save_ = os.path.join(save_folder,folder_name,f"picture_{index}.webp")
            task = asyncio.ensure_future(download(session,url,save_))
            tasks.append(task)
        await asyncio.gather(*tasks)

        return os.path.join(save_folder,folder_name)


def zip_folder(archive_path):

    img_format = (".webp",".png",".jpeg",".jpg")

    files = [
        os.path.join(archive_path, x)
        for x in os.listdir(archive_path)
        if x.endswith(img_format)
    ]

    archive_name = os.path.basename(archive_path)

    with zf.ZipFile(os.path.join(archive_path,f"{archive_name}.zip"),"w") as zipf:
        for file in files:
            zipf.write(file) # Ignore

    for f in files:
        try:
            os.remove(f)
        except:
            pass


    return os.path.join(archive_path,f"{archive_name}.zip")


def delete_old_dl(folder_path):

    shutil.rmtree(folder_path)


async def download_and_zip(urls,name):
    name = re.sub(r"[\\/:*?'<>|\x00]", "_", name)
    name = name.strip()

    file_save_location = await download_asyncly(urls,name)

    zipped_file_path = zip_folder(file_save_location)

    return zipped_file_path


async def delete_folder_later(folder_path, delay=3):
    delay = delay * 60 * 10
    await asyncio.sleep(delay)

    folder_path = os.path.join(save_folder,folder_path)

    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"[AUTO DELETE] Deleted folder: {folder_path}")


