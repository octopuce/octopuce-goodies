#!/usr/bin/env python
#(@)facts2sshfp.py (C) February 2012, by Jan-Piet Mens <jpmens@gmail.com>
# (C) August 2014, by benjamin Sonntag <benjamin@octopuce.fr> for (non-mandatory) ECDSA keys
# with inspiration from Pieter Lexis
#
# Slurp through the YAML fact files collected on a Puppet master,
# extract the SSH RSA/DSA public keys and produce SSHFP records for DNS.
# See also: http://jpmens.net/2011/07/21/it-s-a-fact-in-puppet/
#      and: http://jpmens.net/2012/02/01/on-collecting-ssh-host-keys-for-sshfp-dns-records/
#
# This program contains create_sshfp, which I swiped from Paul Wouter's SSHFP at
# http://www.xelerance.com/services/software/sshfp/. I have removed the hostname
# magic, because not needed here, as we know the fqdn (hopefully)


import glob
import sys, re
import yaml
import json
import codecs
import base64
try:
    import hashlib
    digest = hashlib.sha1
except ImportError:
    import sha
    digest = sha.new
import string
from string import Template
import optparse

factsdir = '/var/lib/puppet/yaml/facts'

def create_sshfp(hostname, keytype, keyblob):
	"""Creates an SSH fingerprint"""

	if keytype == "ssh-rsa":
		keytype = "1"
	else:
		if keytype == "ssh-dss":
			keytype = "2"
		else:
                    if keytype == "ssh-ecdsa":
                        keytype = "3"
                    else:
			return ""
	try:
		rawkey = base64.b64decode(keyblob)
	except TypeError:
		print >> sys.stderr, "FAILED on hostname "+hostname+" with keyblob "+keyblob
		return "ERROR"

	fpsha1 = digest(rawkey).hexdigest().upper()

        # return hostname + " IN SSHFP " + keytype + " 1 " + fpsha1
        return {
            "keytype"   : keytype,
            "fpsha1"    : fpsha1
        }

def facts_to_dict(filename):
    """
    Return dict from YAML contained in filename, having removed the
    fugly Ruby constructs added by Puppet.
    (e.g. --- !ruby/object:Puppet::Node::Facts) which no YAML
    """

    searchregex = "!ruby.*\s?"
    cregex = re.compile(searchregex)

    # "--- !ruby/sym _timestamp": Thu Jan 12 12:25:02 +0100 2012
    # !ruby/sym _timestamp: Tue Oct 04 07:56:54 +0200 2011
    rubyre = '"?(--- )?!ruby/sym ([^"]+)"?:\s+(.*)$'
    nrub = re.compile(rubyre)


    stream = ''
    for line in open(filename, 'r'):

        # Pieter reports his fact files contain e.g. ec2_userdata with binary blobs in them
        # Remove all that binary stuff....

        line = filter(lambda x: x in string.printable, line)
        if nrub.search(line):
            line = nrub.sub(r'\2: \3', line)
        if cregex.search(line):
            line = cregex.sub("\n", line)
        stream = stream + line

    yml = yaml.load(stream)
    return yml['values']

if __name__ == '__main__':

    naming = 'fqdn'
    domainname = ''
    template = ''
    keylist = []

    parser = optparse.OptionParser()
    parser.add_option('-d', '--directory', dest='factsdir', help='Directory containing facts')
    parser.add_option('-H', '--hostname',  dest='usehost', default=False, help='Use hostname i/o fqdn',
        action='store_true')
    parser.add_option('-D', '--domainname', dest='domainname', help='Append domain')
    parser.add_option('-Q', '--qualify', dest='qualify', default=False, help='Qualify hostname with dot', action='store_true')
    parser.add_option('-J', '--json', dest='jsonprint', default=False, help='Print JSON', action='store_true')
    parser.add_option('-Y', '--yaml', dest='yamlprint', default=False, help='Print YAML', action='store_true')
    parser.add_option('-T', '--template', dest='templatename', help='Print using template file')


    (opts, args) = parser.parse_args()

    if opts.factsdir:
        factsdir =  opts.factsdir
    if opts.usehost:
        naming = 'hostname'
    if opts.domainname:
        domainname = opts.domainname
    if opts.templatename:
        template = open(opts.templatename, 'r').read()

    for filename in glob.glob(factsdir + "/*.yaml"):
        facts = facts_to_dict(filename)

        item = {}
        rsa = create_sshfp(facts[naming], 'ssh-rsa', facts['sshrsakey'])
        if 'sshdsakey' in facts:
            dsa = create_sshfp(facts[naming], 'ssh-dss', facts['sshdsakey'])
        else:
            dsa = 0
        if 'sshecdsakey' in facts:
            ecdsa = create_sshfp(facts[naming], 'ssh-ecdsa', facts['sshecdsakey'])
        else:
            ecdsa = 0

        item['hostname']        = facts['hostname']
        item['fqdn']            = facts['fqdn']
        if domainname != '':
            item['domain']          = domainname
        else:
            item['domain']          = facts['domain']

        if naming == 'hostname':
            owner = item['hostname']
        else:
            owner = item['hostname'] + '.' + item['domain']
        if opts.qualify == True:
            owner = owner + '.'
        item['owner']           = owner

        item['rsa_fp']          = rsa['fpsha1']
        item['rsa_keytype']     = rsa['keytype']
        if dsa:
            item['dsa_fp']          = dsa['fpsha1']
            item['dsa_keytype']     = dsa['keytype']
        if ecdsa:
            item['ecdsa_fp']          = ecdsa['fpsha1']
            item['ecdsa_keytype']     = ecdsa['keytype']

        keylist.append(item)

    if opts.jsonprint == True:
        print json.dumps(keylist, indent=4)
    elif opts.yamlprint == True:
        print yaml.dump(keylist, default_flow_style=False, explicit_start=True)
    elif opts.templatename:
        for item in keylist:
            s = Template(template)
            print s.substitute(item)
    else:
        for item in keylist:
            print "%-20s IN SSHFP %s 1 %s" % (item['owner'], item['rsa_keytype'], item['rsa_fp'])
            print "%-20s IN SSHFP %s 1 %s" % (item['owner'], item['dsa_keytype'], item['dsa_fp'])
            if 'ecdsa_fp' in item:
                print "%-20s IN SSHFP %s 1 %s" % (item['owner'], item['ecdsa_keytype'], item['ecdsa_fp'])

