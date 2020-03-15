#!/usr/bin/python

# A simple echo server.  You send it some mail and it sends it right
# back.

# The way this works is it reads a full mime encoded multipart email.
# It expects there to be a text part of that email. It parses the email
# It writes out a full message body that Mutt can send as a normal mail
# body. This program writes out headers, recipient, subject etc all in
# the output.

# To debug this, call it from the commandline with a single multipart email
# and then see the output.

# Normally called from command.sh which looks at the output file, and then
# calls mutt on it.

from email.parser import Parser
from optparse import OptionParser
from time import gmtime, strftime

# Parse the commandline arguments
parser = OptionParser()
parser.add_option("-i", "--input-mail", action="store", type="string", dest="input_mail",
                  help="File containing the multipart email with headers")

parser.add_option("-o", "--output-body", action="store", type="string", dest="output_body",
                  help="Name of the file to write the body of the message")

(options, args) = parser.parse_args()

# Open the output files
output_body = open (options.output_body, "a")
input_mail = Parser().parse(open(options.input_mail, 'r'))

to_address = input_mail['to']

# If the input address was "API hostname <api@hostname.com>", then we want to only retain the api@hostname.com>"
# in the address for the mailboxes to work.
if to_address.find('<') >= 0:
    to_address = to_address[to_address.find('<')+1:]


# Which specific mailbox was this sent to?
# The mailbox name for api+first@hostname.com is first

prefix = 'api'

# Git rid of the @ and everything after that, if it exists.
end_pos = to_address.find('@')
if end_pos >= 0:
    to_address = to_address[:end_pos]

mailbox = to_address[len(prefix)+1:end_pos]
# If the mailbox is empty, call it default
if len(mailbox) == 0:
    mailbox = 'default'


# Try using  mutt -H to encapsulate all the mail information in one place.
header = 'To: %s\n' % input_mail['from']
header += 'Subject: %s\n' % input_mail['subject']
# So threading works correctly
header += 'In-Reply-To: %s' % input_mail['message-id']
header += 'References: %s' % input_mail['message-id']

output_body.write(header)

# TODO(viki): Install the application in a specific mailbox at api+mailbox@hostname.com

# The first part of a multipart message or the string object is the human readable message
if (input_mail.is_multipart()):
    # Can verify that input_mail.get_payload()[0].get_content_type() == 'text/plain'
    input_body = input_mail.get_payload()[0].get_payload()
else:
    input_body = input_mail.get_payload()


localtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
body = "This is command.py.\nThe time is %s.\n" % localtime
body += "The mailbox was %s\n" % mailbox
body += "You said this to me: %s\n----\n\nYour entire message follows:\n" % input_body

sender = ''
input_file = open(options.input_mail, 'r')

for line in input_file.readlines():
    # Append everything to the body, including the header.
    # TODO(viki): Figure out how to just send the body.
    body += line



# Now that the header is written, write the remaining body.
output_body.write(body)
output_body.close()
