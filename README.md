# Cars-and-Bids
A data engineering project that collects, processes, and stores auction data from the [Cars and Bids website](https://carsandbids.com/). This project showcases the use of web scraping, data cleaning, and storage techniques to gather valuable insights about the auction process.
## Overview
The project consists of the following components:

**Web Scraping:** A web scraping script written in Python using Selenium library to extract auction data from the Cars and Bids website. The script navigates through auction pages, collects relevant information, and saves it for further processing.

**Data Cleaning:** The collected data is processed and cleaned using Python and pandas within AWS Lambda functions. The Lambda function is designed to handle the data cleaning tasks, including handling missing values, transforming data types, removing duplicates, and performing other necessary data cleaning operations.

**Storage:** The cleaned data is stored in an Amazon S3 bucket for easy access and further analysis. The project utilizes the AWS S3 service to securely store and manage the auction data.

## Project Structure
The project repository is organized as follows:

├── auctions.py              # Script for web scraping Cars and Bids website<br>
├── upload.py                # Script for uploading collected data to S3<br>
├── jobs.sh                  # Shell script for cron job<br>
├── requirements.txt         # Required Python packages<br>
├── README.md                # Project documentation (you're reading it!)<br>
