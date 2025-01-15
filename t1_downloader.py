import os
import time
import requests
from typing import Dict, Optional
import argparse

# importing basic web selection tools
import yt_dlp
from bs4 import BeautifulSoup as bs

# Importing Selenium tools
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class NPTELDownloader:
    """Class to handle downloading of NPTEL course transcripts"""
    
    def __init__(self, course_url: str, download_folder: str = 'downloads'):
        """
        Initialize the downloader with course URL
        
        Args:
            course_url: URL of the NPTEL course page
            download_folder: Path where downloaded files will be saved
        """
        self.course_url = course_url
        self.download_folder = download_folder
        self.driver = None
        self.wait = None
        self.transcript_download_links = {}
        self.lecture_download_links = {}
        self.tab_number = 1

    def setup_driver(self) -> None:
        """Initialize and setup the Chrome WebDriver"""
        self.driver = webdriver.Chrome()
        self.driver.get(self.course_url)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 20)
        self.tab_number = 1

    def click_initial_buttons(self, tab_name: str) -> None:
        """Click the course details and transcript buttons"""
        course_details_button = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/app-root/app-course-details/main/section/app-course-detail-ui/div/div[2]/span[2]")))
        course_details_button.click()

        # Wait for the button element to be present and find the correct tab
        while True:
            try:
                section_button = self.wait.until(EC.presence_of_element_located(
                            (By.XPATH, f"/html/body/app-root/app-course-details/main/section/app-course-detail-ui/div/div[3]/app-course-downloads/div/div[{self.tab_number}]/div[1]")))
                # Only click if it contains tab_name text
                if tab_name in section_button.text:
                    section_button.click()
                    break
                self.tab_number += 1
            except:
                print(f"{tab_name} button not found after checking all tabs")
                break

    def handle_language_dropdown(self, lec_index: int) -> bool:
        """
        Handle clicking and selecting options in language dropdown
        
        Args:
            lec_index: Index number of the dropdown to handle
            
        Returns:
            bool: True if successful, False if dropdown not found
        """
        try:
            dropdown_xpath = f"/html/body/app-root/app-course-details/main/section/app-course-detail-ui/div/div[3]/app-course-downloads/div/div[{self.tab_number}]/div[2]/div[{lec_index}]/div[1]/app-nptel-dropdown/div"
            language_dropdown_button = self.wait.until(EC.presence_of_element_located((By.XPATH, dropdown_xpath)))
            language_dropdown_button.click()

            self._retry_click_language_option(lec_index)
            self._retry_get_transcript_download_link(lec_index)
            return True

        except Exception as e:
            print(f"No more language dropdowns found after {lec_index-1} dropdowns")
            return False
    
    def handle_lecture_tab(self, lec_index: int) -> bool:
        """
        Handle getting download links from lecture tab

        Args:
            lec_index: Index number of the dropdown to handle

        Returns:
            bool: True if successful, False if lecture download link not found
        """
        try:
            self._retry_get_lecture_download_link(lec_index)
            return True

        except Exception as e:
            print(f"No more lecture dropdowns found after {lec_index-1} dropdowns")
            return False

    def _retry_click_language_option(self, lec_index: int, max_attempts: int = 3) -> None:
        """
        Retry mechanism for clicking language options
        
        Args:
            lec_index: Index of current dropdown
            max_attempts: Maximum number of retry attempts
        """
        attempt = 0
        while attempt < max_attempts:
            try:
                print(f"Attempt {attempt + 1} to click language option for dropdown {lec_index}")
                option_xpath = f"/html/body/app-root/app-course-details/main/section/app-course-detail-ui/div/div[3]/app-course-downloads/div/div[{self.tab_number}]/div[2]/div[{lec_index}]/div[1]/app-nptel-dropdown/ul/li"
                
                option_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
                option_element.click()
                print(f"Successfully clicked language option for dropdown {lec_index}")
                break
            except Exception as e:
                attempt += 1
                print(f"Attempt {attempt} failed for dropdown {lec_index}")
                time.sleep(1)
                if attempt == max_attempts:
                    raise Exception(f"Failed to interact with element after {max_attempts} attempts: {str(e)}")

    def _retry_get_transcript_download_link(self, lec_index: int, max_attempts: int = 5) -> None:
        """
        Retry mechanism for getting download links
        
        Args:
            lec_index: Index of current dropdown
            max_attempts: Maximum number of retry attempts
        """
        attempt = 0
        while attempt < max_attempts:
            try:
                download_xpath = f"/html/body/app-root/app-course-details/main/section/app-course-detail-ui/div/div[3]/app-course-downloads/div/div[{self.tab_number}]/div[2]/div[{lec_index}]/div[2]/a"
                download_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, download_xpath)))
                
                download_url = download_link.get_attribute('href')
                file_id = download_url.split('/')[5]
                direct_url = f'https://drive.google.com/uc?export=download&id={file_id}'
                
                self.transcript_download_links[file_id] = direct_url
                print(f"Download link stored for file ID: {file_id}")
                break
                
            except Exception as e:
                attempt += 1
                print(f"Attempt {attempt} failed to download file for {file_id}")
                time.sleep(1)
                if attempt == max_attempts:
                    raise Exception(f"Failed to get download link after {max_attempts} attempts: {str(e)}")
    
    def _retry_get_lecture_download_link(self, lec_index: int, max_attempts: int = 3) -> None:
        """
        Retry mechanism for getting download links for lectures
        
        Args:
            lec_index: Index of current dropdown
            max_attempts: Maximum number of retry attempts
        """
        attempt = 0
        while attempt < max_attempts:
            try:
                download_xpath = f"/html/body/app-root/app-course-details/main/section/app-course-detail-ui/div/div[3]/app-course-downloads/div/div[{self.tab_number}]/div[2]/div[{lec_index}]/div/a"
                download_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, download_xpath)))
                
                download_url = download_link.get_attribute('href')
                filename = download_url.split('/')[-1]  # Get the mp4 filename
                
                self.lecture_download_links[filename] = download_url
                print(f"Download link stored for file: {filename}")
                break
                
            except Exception as e:
                attempt += 1
                print(f"Attempt {attempt} failed to get download link")
                time.sleep(1)
                if attempt == max_attempts:
                    raise Exception(f"Failed to get download link after {max_attempts} attempts: {str(e)}")

    def download_transcript_files(self) -> None:
        """Download all files from collected download links"""
        if not os.path.exists(os.path.join(self.download_folder, 'transcripts')):
            os.makedirs(os.path.join(self.download_folder, 'transcripts'))
            
        for file_id, url in self.transcript_download_links.items():
            try:
                session = requests.Session()
                response = session.get(url, stream=True)
                
                filename = self._get_filename(response, file_id)
                filepath = os.path.join(self.download_folder, 'transcripts', filename)
                
                self._save_file(response, filepath)
                print(f'Successfully downloaded {filename}')
                
            except Exception as e:
                print(f'Failed to download file {file_id}: {str(e)}')
                continue
                
            time.sleep(1)
        
    
    def download_lecture_files(self) -> None:
        """Download all files from collected download links"""
        if not os.path.exists(os.path.join(self.download_folder, 'lectures')):
            os.makedirs(os.path.join(self.download_folder, 'lectures'))
            
        for filename, url in self.lecture_download_links.items():
            try:
                
                filepath = os.path.join(self.download_folder, 'lectures', filename)

                ydl_opts = {
                    'format': 'bestaudio/best',
                    'extractaudio': True,  
                    'audioformat': 'mp3', 
                    'outtmpl': filepath, 
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',  # Use FFmpeg to process audio
                        'preferredcodec': "mp3", 
                        'preferredquality': '0', 
                    }],
                }

                # Download audio
                yt_dlp.YoutubeDL(ydl_opts).download([url])
                
                print(f'Successfully downloaded {filename}')
                
            except Exception as e:
                print(f'Failed to download file {filename}: {str(e)}')
                continue
                
            time.sleep(1)

    def _get_filename(self, response: requests.Response, file_id: str) -> str:
        """Extract filename from response headers or generate default name"""
        if 'content-disposition' in response.headers:
            return response.headers['content-disposition'].split('filename=')[1].strip('"')
        return f'{file_id}.txt'

    def _save_file(self, response: requests.Response, filepath: str) -> None:
        """Save downloaded file to disk"""
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    def download_transcripts(self) -> None:
        """Main method to run the complete download process for transcripts"""
        try:
            self.setup_driver()
            self.click_initial_buttons(tab_name='Transcripts')
            
            n = 2
            while self.handle_language_dropdown(n):
                n += 1
                
            self.download_transcript_files()
            
        finally:
            if self.driver:
                self.driver.quit()
    
    def download_lectures(self) -> None:
        """Main method to run the complete download process for lectures"""
        try:
            self.setup_driver()
            self.click_initial_buttons(tab_name='Videos')
            
            n = 2
            while self.handle_lecture_tab(n):
                n += 1
                
            self.download_lecture_files()
            
        finally:
            if self.driver:
                self.driver.quit()

def main(course_url, download_dir, download_type):
    """Main entry point of the script"""
    downloader = NPTELDownloader(course_url, download_dir)
    
    if download_type == '-t':
        downloader.download_transcripts()
    elif download_type == '-l':
        downloader.download_lectures()
    else:  # default case is '-tl'
        downloader.download_lectures()
        downloader.download_transcripts()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download NPTEL course lectures and/or transcripts.")
    parser.add_argument('course_url', help="The URL of the NPTEL course.")
    parser.add_argument('download_dir', help="The directory where the lectures should be saved.")
    
    # Optional argument for download type (-t for transcripts, -l for lectures, -tl for both)
    parser.add_argument('-d', '--download_type', choices=['-t', '-l', '-tl'], default='-tl', 
                        help="Choose download type: '-t' for transcripts, '-l' for lectures, '-tl' for both (default is '-tl').")

    args = parser.parse_args()

    main(args.course_url, args.download_dir, args.download_type)



    
