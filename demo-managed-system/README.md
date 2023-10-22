This is a small node.js based server used to test and demonstrate the basic functionality of UPISAS.

Steps to use it: 
1. Get Node.js
2. Install libraries with ``npm install`` (only needed once) 
3. Start the server with ``node app.js`` 

Then open a new terminal tab or window and run UPISAS.

If you do any changes to the managed system, then run 
1. `docker build . -t <dockerhub username>/upisas-demo-managed-system`
2. Update the "image" in DemoExemplar to point to `<dockerhub username>/upisas-demo-managed-system`
