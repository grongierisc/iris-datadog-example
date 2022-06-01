from iris.pex import Director
import iris

connection = iris.connect(hostname="localhost", port=51773, namespace="USER", username="SuperUser", password="SYS", sharedmemory = False,timeout=10,logfile='/Users/grongier/git/iris-datadog-example/py.log')
irisInstance = iris.IRIS(connection)
irisobject = irisInstance.classMethodObject("EnsLib.PEX.Director","dispatchCreateBusinessService","Python.FlaskService")
service = iris.pex._IRISBusinessService._IRISBusinessService()
service = Director.CreateBusinessService(connection,"Ens.BusinessMetric")
response = service.ProcessInput('msg')