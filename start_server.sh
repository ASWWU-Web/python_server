sleep 1;
screen -Sdm ps1 python server.py --port=8881
sleep 1;
screen -Sdm ps2 python server.py --port=8882
sleep 1;
screen -Sdm ps3 python server.py --port=8883
sleep 1;
screen -Sdm ps4 python server.py --port=8884
