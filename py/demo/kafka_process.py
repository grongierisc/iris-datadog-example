
import iris.pex
import iris
import logging
from ddtrace import patch_all,tracer
patch_all()

class KafkaProcess(iris.pex.BusinessProcess):

    @tracer.wrap()
    def OnInit(self):
        logging.info("[Python] ...KafkaProcess:OnInit() is called")
        return

    @tracer.wrap()
    def OnTearDown(self):
        logging.info("[Python] ...KafkaProcess:OnTearDown() is called")
        return

    @tracer.wrap()
    def OnRequest(self, request):
        # called from business service, message is of type Ens.StringContainer with property StringValue
        try:
          value = int(request.get("StringValue"))
          logging.info("[Python] ...KafkaProcess:OnRequest() is called wth request: " + str(value))
        except:
          logging.error("[Python] ...Unable to convert request to int.")  
          return
        if value > 0:
          callrequest = iris.GatewayContext.getIRIS().classMethodObject("dc.KafkaRequest", "%New")
          callrequest.set("Topic", self.TOPIC)
          callrequest.set("Text", str(value - 1))
          self.SendRequestAsync(self.TargetConfigName, callrequest, False)
        elif value == -1:
          callrequest = iris.GatewayContext.getIRIS().classMethodObject("dc.KafkaRequest", "%New")
          callrequest.set("Topic", self.TOPIC)
          callrequest.set("Text", str(-1))
          self.SendRequestAsync(self.TargetConfigName, callrequest, False)
        else:
          logging.error("[Python] ...KafkaProcess:OnRequest() value is not a positive int. Exit.")
        return

    @tracer.wrap()
    def OnResponse(self, request, response, callRequest, callResponse, pCompletionKey):
        logging.info("[Python] ...KafkaProcess:OnResponse() is called")
        return

    @tracer.wrap()
    def OnComplete(self, request, response):
        logging.info("[Python] ...KafkaProcess:OnComplete() is called")
        return