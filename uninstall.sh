#!/bin/bash
# VideoMorph uninstall script

for i in $(find /usr -path "*videomorph*"); do
	rm -rfv $i
done

