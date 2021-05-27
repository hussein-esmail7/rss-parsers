#! /bin/bash

# html2rss bash version
# Created: 2021 05 16
# Updated: 2021 05 16
# ======= UNFINISHED ========

AUTHOR="Hussein Esmail"
RSS_LABEL="Hussein's Articles"
RSS_TERM="Articles"

MESSAGE_INPUT_HTML="You need to input an HTML file to convert!"
MESSAGE_NOT_AN_INT="I didn't like that input! Please type an int."
MESSAGE_INCORRECT_ARGS="Illegal number of parameters"
MESSAGE_COPIED="Copied to clipboard."

TAG_TITLE_TYPE="h1"

function yes_or_no() {
	# This function asks a question and asks for a yes/no input
	# Keeps asking until it gets a valid input
	# $1 = Question to ask
	while true; do
		read -p "$1" yn
		case $yn in
			[Yy]* ) return 0;; # true
			[Nn]* ) return 1;; # false
				* ) echo "Please answer yes or no.";;
		esac
	done
}

function main() {
	# If number of arguments is not 2, throw error
	if [ "$#" -ne 2 ]; then
		echo "$MESSAGE_INCORRECT_ARGS"
		echo "$#"
		exit 1
	fi
	# If HTML arg does not end in ".html"
	[[ $(echo "$1" | tr '[:upper:]' '[:lower:]') -ne *".html" ]]; \
		echo "First argument must end in '.html'" && exit 1
	
	# If RSS arg does not end in ".xml" or ".rss"
	RSS_FILENAME=$(echo "$2" | tr '[:upper:]' '[:lower:]')
	[[ "$RSS_FILENAME" -ne *".xml" && "$RSS_FILENAME" -ne *".rss" ]]; \
		echo "Second argument must end in '.xml' or '.rss'" && exit 1
	
	is_integer() {
		[[ "$1" =~ ^[[:digit:]]+$ ]]
	}

	echo "Your inputs are valid"

	num_total_lines=$(cat '$1' | wc -l | xargs)
	num_title_line=""
	read -p "First line of the post ($TAG_TITLE_TYPE tag with the title) [/$num_total_lines lines]?" num_title_line
	while ! [[ "$num_title_line" =~ ^[[:digit:]]+$ ]]; do
		read -p "First line of the post ($TAG_TITLE_TYPE tag with the title) [/$num_total_lines lines]?" num_title_line
	done
	
	tail -n +$((num_total_lines-num_title_line)) $1 > .lines_wanted

	head -n ${awk '/<\/body>/{print NR}'} .lines_wanted
	cat .lines_wanted
	
}



main "$1" "$2"










