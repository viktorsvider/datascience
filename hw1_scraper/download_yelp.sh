base_url="https://www.yelp.com/biz/the-porch-at-schenley-pittsburgh"
start=0
end=1010
echo "base_url =" $base_url;
for ((start_i=start; start_i<=end; start_i+=10));
    do 
    download_url="${base_url}?start=${start_i}"
    echo "downloading ?start="$start_i;
    wget $download_url -O "the-porch-at-schenley-pittsburgh_${start_i}"
    sleep 1.5
    done