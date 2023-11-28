import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
import subprocess

def download_file(url, folder):
    response = requests.get(url)
    if response.status_code == 200:
        file_name = os.path.join(folder, url.split("/")[-1])
        with open(file_name, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {file_name}")
        return file_name
    else:
        print(f"Failed to download: {url}")
        return None

def is_supported_file_type(file_path):
    supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.mp4', '.webm'}
    _, file_extension = os.path.splitext(file_path)
    return file_extension.lower() in supported_extensions

def convert_webp_to_png(file_path):
    if not is_supported_file_type(file_path):
        print(f"File type not supported: {file_path}")
        return None

    _, file_extension = os.path.splitext(file_path)
    if file_extension.lower() == '.webp':
        # Convert WebP to PNG
        png_file_path = os.path.splitext(file_path)[0] + '.png'
        im = Image.open(file_path).convert("RGBA")
        im.save(png_file_path, "PNG")
        print(f"Converted {file_path} to {png_file_path}")
        return png_file_path
    else:
        return file_path

def convert_mp4_to_webm(file_path):
    if not is_supported_file_type(file_path):
        print(f"File type not supported: {file_path}")
        return None

    _, file_extension = os.path.splitext(file_path)
    if file_extension.lower() == '.mp4':
        # Convert MP4 to WebM using FFmpeg
        webm_file_path = os.path.splitext(file_path)[0] + '.webm'
        subprocess.run(["ffmpeg", "-i", file_path, webm_file_path])
        print(f"Converted {file_path} to {webm_file_path}")
        return webm_file_path
    else:
        return file_path

def replace_links_in_line(line, old_links, new_links):
    for old_link, new_link in zip(old_links, new_links):
        line = line.replace(old_link, f"https://77rx2b.github.io/3D-models/website/{os.path.basename(new_link)}")
    return line

def extract_urls_from_line(line):
    soup = BeautifulSoup(line, 'html.parser')
    img_urls = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith("https://cdn.discordapp.com")]
    img_urls += [img['src'] for img in soup.find_all('img', {'src': True}) if img['src'].startswith("https://cdn.discordapp.com")]
    video_urls = [source['src'] for source in soup.find_all('source', {'src': True}) if source['src'].startswith("https://cdn.discordapp.com")]
    return img_urls + video_urls

def main(input_file, output_folder):
    with open(input_file, 'r', encoding='utf-8') as file:
        new_lines = []
        old_links = []
        new_links = []
        
        for line in file:
            urls = extract_urls_from_line(line)
            for url in urls:
                file_path = download_file(url, output_folder)
                if file_path and is_supported_file_type(file_path):
                    file_path = convert_webp_to_png(file_path)
                    file_path = convert_mp4_to_webm(file_path)
                    if file_path:
                        old_links.append(url)
                        new_links.append(file_path)

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
