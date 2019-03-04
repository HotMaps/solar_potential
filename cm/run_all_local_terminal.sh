#!/usr/bin/env bash


sudo gnome-terminal -e "python consumer_cm_alive.py" --title="solar_potential: consumer_cm_alive"

sudo gnome-terminal -e "python3 run.py" --title="solar_potential: run CM"

sudo gnome-terminal -e "python3 consumer_cm_compute.py" --title="solar_potential: consumer_cm_compute_solar_potential"

sudo gnome-terminal -e "python3 register_cm.py" --title="solar_potential: register_cm"



