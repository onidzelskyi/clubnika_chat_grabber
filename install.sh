apt-get install python-pip python-dev python-lxml unzip libffi-dev libssl-dev libxml2-dev libxslt1-dev xvfb
pip install scrapy w3lib cssselect selenium python-dateutil pyvirtualdisplay requests

#chromedriver
#https://sites.google.com/a/chromium.org/chromedriver/home
wget http://chromedriver.storage.googleapis.com/2.20/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
rm *.zip
chmod a+x chromedriver