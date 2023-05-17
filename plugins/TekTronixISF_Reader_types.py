import enum
import plugins.common_basetypes

@enum.unique
class ISFElements(enum.IntEnum) : 

        ISF_BYT_NR  = 0
        ISF_BIT_NR  = 1 + ISF_BYT_NR
        ISF_NR_PT   = 1 + ISF_BIT_NR
        ISF_PT_OFF  = 1 + ISF_NR_PT
        ISF_XINCR   = 1 + ISF_PT_OFF
        ISF_XZERO   = 1 + ISF_XINCR
        ISF_XUNIT   = 1 + ISF_XZERO
        ISF_YMULT   = 1 + ISF_XUNIT
        ISF_YZERO   = 1 + ISF_YMULT
        ISF_YOFF    = 1 + ISF_YZERO
        ISF_YUNIT   = 1 + ISF_YOFF
        ISF_ENCDG   = 1 + ISF_YUNIT
        ISF_BN_FMT  = 1 + ISF_ENCDG
        ISF_BYT_OR  = 1 + ISF_BN_FMT
        ISF_PT_FMT  = 1 + ISF_BYT_OR
        ISF_WFID    = 1 + ISF_PT_FMT
        ISF_CURVE   = 1 + ISF_WFID

#end

@enum.unique
class ISFFileElements(enum.IntEnum) :
    ISF_DATA = 0
#end

@enum.unique
class ISFBN_FMTType(plugins.common_basetypes.GenericBaseEnum) :

    ISF_RI  = "RI"
    ISF_RP  = "RP"
    INVALID = -1

#end

@enum.unique
class ISFBYT_ORType(plugins.common_basetypes.GenericBaseEnum) :

    ISF_MSB = "MSB"
    ISF_LSB = "LSB"
    INVALID = -1

#end

@enum.unique
class ISFENCDGType(plugins.common_basetypes.GenericBaseEnum) :

    ISF_BIN = "BIN"
    ISF_ASC = "ASC"
    INVALID = -1

#end
