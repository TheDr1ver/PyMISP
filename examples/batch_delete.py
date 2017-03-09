#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymisp import PyMISP
from keys import misp_url, misp_key,misp_verifycert
import argparse
import os
import json
from pprint import pprint
from sys import version_info


def init(url, key):
    return PyMISP(url, key, misp_verifycert, 'json')


def search(m, quiet, url, controller, out=None, **kwargs):
    #print kwargs
    result = m.search(controller, **kwargs)
    #print result
    if 'response' in result:
        return result['response']
    else:
        print "\r\n\r\n"
        print "Search returned no results!"
        return ''
    '''
    if quiet:
        for e in result['response']:
            print('{}{}{}\n'.format(url, '/events/view/', e['Event']['id']))
    elif out is None:
        for e in result['response']:
            print(json.dumps(e) + '\n')
    else:
        with open(out, 'w') as f:
            for e in result['response']:
                f.write(json.dumps(e) + '\n')
    '''
                

def del_event(m, eventid):
    result = m.delete_event(eventid)
    print(result)
                
                
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Purge all events based on a given search.')
    parser.add_argument("-p", "--param", required=True, help="Parameter to search (e.g. category, org, etc)")
    parser.add_argument("-s", "--search", required=True, help="String to search.")
    parser.add_argument("-a", "--attributes", action='store_true', help="Search attributes instead of events")
    parser.add_argument("-q", "--quiet", action='store_true', help="Only display URLs to MISP")
    parser.add_argument("-o", "--output", help="Output file")

    args = parser.parse_args()

    if args.output is not None and os.path.exists(args.output):
        print('Output file already exists, abort.')
        exit(0)

    misp = init(misp_url, misp_key)
    kwargs = {args.param: args.search}

    if args.attributes:
        controller='attributes'
    else:
        controller='events'

    search_res=search(misp, args.quiet, misp_url, controller, args.output, **kwargs)
    
    #pprint(search_res)
    #search_res=json.dumps(search_res)
    
    if search_res:
        purge_ids=[]
        
        if args.attributes:
            # Do the attributes Event ID search
            for k, v in search_res.iteritems():
                for att in v:
                    #print att
                    if int(att['event_id']) not in purge_ids:
                        purge_ids.append(int(att['event_id']))
        else:
            for event in search_res:
                #print event['Event']['id']
                if int(event['Event']['id']) not in purge_ids:
                    purge_ids.append(int(event['Event']['id']))
        
        '''    
        def id_generator(id_dict):
            if isinstance(id_dict, dict):
                for k,v in id_dict.items():
                    print k
                    if k == 'id':
                        yield v
                    elif isinstance(v,dict):
                        for id_val in id_generator(v):
                            yield id_val
                    elif isinstance(v, list) or isinstance(v, tuple):
                        for x in v:
                            for id_val in id_generator(x):
                                yield id_val
                        
        for event in search_res:
            for id in id_generator(event):
                print id
                purge_ids.append(id)
        '''
        '''
        for event in search_res:
            for attribs, vals in event:
                for k,v in attribs.iteritems():
                    if k=='id':
                        print v
                        purge_ids.append(v)
        '''
        
        print "\r\n\r\n\r\n"
        print "The following event IDs were found from this search."
        print str(purge_ids)
        
        
        py3 = version_info[0] > 2
        if py3:
            response = input("If you are sure you want to delete these events, type 'DELETE THEM':  ")
        else:
            response = raw_input("If you are sure you want to delete these events, type 'DELETE THEM':  ")
            
        if response=="DELETE THEM":
            for id in purge_ids:
                del_event(misp, id)
            print "All events deleted!"
        else:
            print "OK - leaving them alone and exiting now."
    
