import os
import requests
from bs4 import BeautifulSoup

downloaded_files = {}

def download_file(url, folder):
    if url in downloaded_files:
        return downloaded_files[url]

    response = requests.get(url)
    if response.status_code == 200:
        file_name = os.path.join(folder, url.split("/")[-1])
        # Check if the file already exists and add a suffix if needed
        file_name = get_unique_filename(file_name)
        with open(file_name, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {file_name}")
        downloaded_files[url] = file_name
        return file_name
    else:
        print(f"Failed to download: {url}")
        return None

def get_unique_filename(file_path):
    base_name, ext = os.path.splitext(file_path)
    counter = 1
    while os.path.exists(file_path):
        file_path = f"{base_name}_{counter}{ext}"
        counter += 1
    return file_path

def replace_links_in_line(line, old_links, new_links):
    for old_link, new_link in zip(old_links, new_links):
        line = line.replace(old_link, new_link)
    return line

def extract_urls_from_line(line):
    soup = BeautifulSoup(line, 'html.parser')
    img_urls = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith(("https://cdn.discordapp.com", "https://media.discordapp.net"))]
    img_urls += [img['src'] for img in soup.find_all('img', {'src': True}) if img['src'].startswith(("https://cdn.discordapp.com", "https://media.discordapp.net"))]
    video_urls = [source['src'] for source in soup.find_all('source', {'src': True}) if source['src'].startswith(("https://cdn.discordapp.com", "https://media.discordapp.net"))]
    return img_urls + video_urls

def main(input_file, output_folder):
    global downloaded_files
    downloaded_files = {}

    with open(input_file, 'r', encoding='utf-8') as file:
        new_lines = []
        old_links = []
        new_links = []
        
        for line in file:
            urls = extract_urls_from_line(line)
            for url in urls:
                file_path = download_file(url, output_folder)
                if file_path:
                    old_links.append(url)
                    new_links.append(f"https://77rx2b.github.io/3D-models/website/{os.path.basename(file_path)}")

            # Replace old links with new formatted links
            updated_line = replace_links_in_line(line, old_links, new_links)
            new_lines.append(updated_line)

    # Save the updated content to the input file
    with open(input_file, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)

if __name__ == "__main__":
    input_file_path = "blog.txt"  # Replace with the path to your input text file
    output_folder_path = "website"  # Replace with the desired output folder

    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    main(input_file_path, output_folder_path)
