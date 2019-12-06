python3 -m venv venv
source venv/bin/activate
pip3 install setuptools
pip3 install -r requirements.txt
mkdir -p results
cd data
git clone https://github.com/sikorski-as/sndlib.git