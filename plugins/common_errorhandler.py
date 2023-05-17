import sys

def ErrorHandler(kErrorMessage : str, kErrorLevel, kErrorHandling) :

    # Circular Reference...
    import plugins.common_basetypes

    if ((plugins.common_basetypes.ErrorLevelHandling.INFO == kErrorHandling) or
        ((plugins.common_basetypes.ErrorLevel.WARNING == kErrorLevel) and (plugins.common_basetypes.ErrorLevelHandling.NORMAL == kErrorHandling))) :
        print(kErrorMessage, file=sys.stderr)
    else :
        raise TypeError(kErrorMessage)
    #end

#end