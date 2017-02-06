#!/usr/bin/env python

from argparse import ArgumentParser

def build_parser():
    parser = ArgumentParser()
    parser.add_argument('--hello', type=str,
                        dest='is_hello',
                        help='says hello',
                        metavar='HELLO', required=True)

    parser.add_argument('--good', type=str,
                        dest='is_good',
                        help='whether is good',
                        metavar='GOOD', required=True)

    return parser

parser = build_parser()
opts = parser.parse_args()

print opts.is_hello
print opts.is_good