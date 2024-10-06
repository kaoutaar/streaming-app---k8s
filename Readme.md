

# Introduction

The Streaming Bike Data Application utilizes the public JCDECAUX API to deliver real-time insights on bike stations, available bikes, and docking status.

Data is ingested via an Apache Kafka pipeline, allowing for continuous data flow. Processing occurs with Apache Spark structured streaming using Spark Connect, which decouples the data pipeline and streamlines data transformations. After processing, the data is stored in the integrated Spark warehouse, from which it is read and served to the Streamlit web application for visualization.

This interactive app provides user with immediate access to live data on bike availability and station status.

Deployment is orchestrated with Kubernetes (K8s).

Kind is used to create a k8s cluster with 5 virtual nodes locally.




![Image](arch.svg)



# How to?

## Step 1: Install kubectl (the Kubernetes command-line tool)

the steps in the official doc are well described and easy to follow:

https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/#install-kubectl-binary-on-windows-via-direct-download-or-curl


## Step 2: Install Kind

**Windows**:
assuming that you already have Docker installed

 in your CMD:

``curl.exe -Lo kind-windows-amd64.exe https://kind.sigs.k8s.io/dl/v0.11.1/kind-windows-amd64``

``mkdir C:\kind``

``move .\kind-windows-amd64.exe c:\kind\kind.exe``


 
      > make sure you add "c:\kind" to your path variable

**Other OS**:

follow steps [here](https://kind.sigs.k8s.io/docs/user/quick-start/)


## Step 3: Run Docker deamon

## Step 4: Create a cluster with kind

`kind create cluster --config kind-config.yaml`

The default name of the cluster is "kind", you can change it using the flag `--name`


This will bootstrap a Kubernetes cluster of 5 virtual nodes (one master and 4 workers).

to see if your cluster is created and the docker containers are up :

`kind get clusters`

`docker ps -a`

## step 5: Prepare Docker images

All images used in this project are available on docker hub:
- kafka image by bitnami
- zookeeper image by bitnami
- spark (a custom image built on top of spark image by bitnami and pushed to dockerhub)
- myapp (a custom image built on top of python image and pushed to docker hub)

Docker files and necessary code used to build the custom images are available to you in `src`

If you want to customize further the images or just rebuild your own versions, you have to push them to a private or public registry like dockerhub so that K8s can pull them out afterwards. 


**how to push to dockerhub?**

- build the custom image first, for example:

``docker build -t myapp:1.0 ./src/APP``

then:

- ``docker login``

- enter your ``username`` and ``password``

- ``docker tag myapp:1.0 <username>/myapp:1.0``

- ``docker push <username>/myapp:1.0``

## step 6: prepare the yaml files

Now the images are ready, we need to build our yaml files and set the configuration of each pod in the cluster, one pod per node and one service per pod.

## step : interact with the cluster using kubectl

Make sure all the containers are up and run in order

```
kubectl apply -f ./yamls/zookeeper.yaml
kubectl apply -f ./yamls/kafka.yaml
kubectl apply -f ./yamls/spark.yaml

#wait until previous deployments are ready before launching the app

kubectl apply -f ./yamls/app.yaml
```

To check that all pods and services are running:

``kubectl get pods``


``kubectl get svc``


If all pods are ``READY`` , now you can access the app from your browser, to do so, redirect the traffic to a port in your machine:

``kubectl port-forward service/app 8501:8501``

Voila! the app is available at:


      localhost:8501


### Tips to debug:
in case you encounter an error with a pod:

* `kubectl describe pod <pod-name>`

* `kubectl logs <pod-name>`

* to open a direct terminal inside the container: ``kubectl exec -it <pod-name> -- /bin/sh`` 