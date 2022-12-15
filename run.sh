#!/bin/bash
echo "################ VisionOne to Elastic. ################"
echo ""
echo ""
echo ""
echo "Provide your VisionOne Authentication token."
echo "Ready:Core@Container:>"
echo "Ready:Core@Container:>${1} : added."
echo "Ready:Core@Container:>ELastic server IP ${2} : added."
export TMV1_TOKEN="${1}"
export TMV1_ELASTIC_HOST="${2}"
sleep 10
echo "Ready:Core@Container:> RUNNING VisionOne import every 60 minutes.........."

while true; do python3 main.py ;date ; sleep 3600; done
