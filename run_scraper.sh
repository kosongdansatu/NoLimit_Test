#!/bin/bash

# Memastikan setidaknya satu argumen diberikan
if [ $# -lt 1 ]; then
  echo "Usage: $0 [phrase] [proxy_url]"
  exit 1
fi

# Menjalankan script Python dengan argumen yang diberikan
phrase=$1
proxy_url=$2

if [ -z "$proxy_url" ]; then
  python3 scraper.py "$phrase"
else
  python3 scraper.py "$phrase" "$proxy_url"
fi
