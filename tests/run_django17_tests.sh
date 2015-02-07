#!/bin/sh

set -e

cd tests/django17
$1 manage.py test
