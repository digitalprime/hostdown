import natural
import natural.date
import natural.number
import webhelpers
import markdown
import webhelpers.date
import webhelpers.number
import webhelpers.text


def time_ago_in_words(value):
	return natural.date.duration(value)


def format_number(value):
	return webhelpers.number.format_number(value)


def markdown_file(value):
	try:
		with open(value, "r") as f:
			data = f.read()
		return markdown.markdown(data, extensions=['markdown.extensions.smarty'])
	except IOError as e:
		return e.message


def urlshort(value):
	if value:
		p = value.find('//')
		if p:
			return (value[p+2:]).rstrip('/')

	return 'o_O'
