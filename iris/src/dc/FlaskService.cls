Class dc.FlaskService Extends Ens.BusinessService
{

Property TargetConfigNames As %String(MAXLEN = 1000) [ InitialExpression = "KafkaProcess" ];

Parameter SETTINGS = "TargetConfigNames:Basic:selector?multiSelect=1&context={Ens.ContextSearch/ProductionItems?targets=1&productionName=@productionId}";

Method OnProcessInput(pDocIn As %RegisteredObject, Output pDocOut As %RegisteredObject) As %Status
{
    set status = $$$OK

    try {
        set msg = ##class(Ens.StringRequest).%New(pDocIn)
        for iTarget=1:1:$L(..TargetConfigNames, ",") {
		    set tOneTarget=$ZStrip($P(..TargetConfigNames,",",iTarget),"<>W")  Continue:""=tOneTarget
		    $$$ThrowOnError(..SendRequestSync(tOneTarget,msg,.pDocOut))
	    }
    } catch ex {
        set status = ex.AsStatus()
    }

    Quit status
}

}
