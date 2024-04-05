#!/bin/bash

# Small script to install Zig into a PyPA manylinux2014 Docker container

apt-get update && apt-get install -y wget xz-utils

arch=$(uname -m)

if [ "$arch" == "x86_64" ]; then
    tarball="zig-linux-x86_64-0.11.0.tar.xz"
elif [ "$arch" == "aarch64" ] || [ "$arch" == "arm64" ]; then
    tarball="zig-linux-aarch64-0.11.0.tar.xz"
else
    echo "Unsupported architecture: $arch"
    exit 1
fi

wget "https://ziglang.org/download/0.11.0/$tarball"
mkdir -p "$HOME/zig_installed/"
tar -C "$HOME/zig_installed/" -xf "$tarball"
rm "$tarball"  # Remove the downloaded tarball after extraction

echo 'export PATH=$PATH:$HOME/zig_installed/' >> ~/.bashrc
echo 'export PATH=$PATH:$HOME/zig_installed/' >> ~/.bash_profile

source ~/.bashrc
source ~/.bash_profile

# zig version
