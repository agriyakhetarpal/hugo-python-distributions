# !#/bin/bash

# Small script to install Golang into a PyPA manylinux2014 Docker container

yum install -y wget

arch=$(uname -m)

if [ "$arch" == "x86_64" ]; then
    tarball="go1.21.6.linux-amd64.tar.gz"
elif [[ "$arch" == "aarch64" || "$arch" == "arm64" ]]; then
    tarball="go1.21.6.linux-arm64.tar.gz"
else
    echo "Unsupported architecture: $arch"
    exit 1
fi

wget https://golang.org/dl/$tarball
mkdir $HOME/go_installed/
tar -C $HOME/go_installed/ -xzf $tarball
export PATH=$PATH:$HOME/go_installed/go/bin >> ~/.bashrc
export PATH=$PATH:$HOME/go_installed/go/bin >> ~/.bash_profile
go version
