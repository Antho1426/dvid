# deal with special characters
export LANG=en_GB.UTF-8

IFS=$'\n'

# set notifications
notification() {
  ./_licensed/terminal-notifier/terminal-notifier.app/Contents/MacOS/terminal-notifier -title "DownVid" -message "${1}"
}

# update youtube-dl if it's more than 15 days old
if [[ $(find youtube-dl -mtime +15) ]]; then
  python youtube-dl --update
fi

gettitle() {
  # file location
  filename=$(python youtube-dl --no-playlist --output "${downdir}/%(title)s.%(ext)s" --get-filename "${link}")

  # title
  title=$(basename ${filename%.*})

  # check if url is valid
  if [[ -z "${filename}" ]]; then
    notification "The url is invalid"
    exit 1
  else
    notification "Downloading “${title}”"
  fi
}

getfile() {
  progressfile="/tmp/downvidprogress"

  python youtube-dl --no-playlist --newline --output "${downdir}/%(title)s.%(ext)s" "${link}" > "${progressfile}"

  # add metadata
  xmlencodedurl=$(echo "${link}" | perl -MHTML::Entities -CS -pe'$_ = encode_entities($_, q{&<>"'\''})')
  xattr -w com.apple.metadata:kMDItemWhereFroms '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"><plist version="1.0"><array><string>'"${xmlencodedurl}"'</string></array></plist>' "${filename}"

  rm "${progressfile}"
}

# download
if [[ "{query}" == "addToWatchList"* ]]; then
  watchlist="${HOME}/Library/Application Support/Alfred 2/Workflow Data/com.vitorgalvao.alfred.watchlist/towatch.txt"
  link=$(cat "$(echo {query} | sed 's/addToWatchList //')")
  downdir="${HOME}/Downloads"
  gettitle
  getfile
  printf "${filename}\n$(cat "${watchlist}")" > "${watchlist}"
else
  link="$(cat {query})"
  downdir="${HOME}/Desktop"
  gettitle
  getfile
fi

notification "Downloaded “${title}”"