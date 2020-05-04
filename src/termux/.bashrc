##
# this function downloads $1 ;)
##
function yt
{
  nohup youtube-dl "$1" --no-progress 2>&1 > /dev/null & 
}

###
# this script returns the deeplink of $1 
###
function yl
{
  deep_link=`youtube-dl -g "$1" -f 18`
  echo "deep_link: $deep_link"
  #deep_link=$deep_link  | sed -e 's/^https/http/g'
  #echo $deep_link
  deep_link=${deep_link//https:/http:}
  youtube-dl -f 18 "$1"
  #for i in `seq 1 10`;
  #  do
  #    #wget -c    "$deep_link"
  #    youtube-dl -f 18 "$1"
  #  done
}

export PS1='\u@\h:\W$ '

