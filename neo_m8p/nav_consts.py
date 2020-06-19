'''
constants named by their mnemonic from the UBX message doc: https://www.u_blox.com/en/docs/UBX_13003221
'''
# mnemonic = [ class, id, length]

ACK_ACK = [0x05, 0x01, 2] # Message acknowledged

ACK_NAK = [0x05, 0x00, 2] # Message not acknowledged

AID_ALM = [0x0B, 0x30, 0] # Poll GPS aiding almanac data

AID_ALM = [0x0B, 0x30, 1] # Poll GPS aiding almanac data for a SV

AID_ALM = [0x0B, 0x30, 8] # (40) Input/Output GPS aiding almanac input/output...

AID_AOP = [0x0B, 0x33, 0] # Poll AssistNow Autonomous data, all...

AID_AOP = [0x0B, 0x33, 1] # Poll AssistNow Autonomous data, one...

AID_AOP = [0x0B, 0x33, 68] # AssistNow Autonomous data

AID_EPH = [0x0B, 0x31, 0] # Poll GPS aiding ephemeris data

AID_EPH = [0x0B, 0x31, 1] # Poll GPS aiding ephemeris data for a SV

AID_INI = [0x0B, 0x01, 0] # Poll GPS initial aiding data

AID_INI = [0x0B, 0x01, 48] # Aiding position, time, frequency, clock...

CFG_ANT = [0x06, 0x13, 4] # Antenna control settings

CFG_BATCH = [0x06, 0x93, 8] # Get/set data batching configuration

CFG_CFG = [0x06, 0x09, 12] # (13) Command Clear, save and load configurations

CFG_DGNSS = [0x06, 0x70, 4] # DGNSS configuration

CFG_DOSC = [0x06, 0x61, 4] # 32*numO...  Get/set Disciplined oscillator configuration

CFG_ESRC = [0x06, 0x60, 4] # 36*numS...  Get/set External synchronization source...

CFG_GEOFENCE = [0x06, 0x69, 8] # 12*numF...  Get/set Geofencing configuration

CFG_GNSS = [0x06, 0x3E, 4] # 8*numCo...  Get/set GNSS system configuration

CFG_HNR = [0x06, 0x5C, 4] # High navigation rate settings

CFG_ITFM = [0x06, 0x39, 8] # Jamming/interference monitor...

CFG_LOGFILTER = [0x06, 0x47, 12] # Data logger configuration

CFG_MSG = [0x06, 0x01, 2] # Poll a message configuration

CFG_MSG = [0x06, 0x01, 8] # Set message rate(s)

CFG_MSG = [0x06, 0x01, 3] # Set message rate

CFG_NAV5 = [0x06, 0x24, 36] # Navigation engine settings

CFG_NAVX5 = [0x06, 0x23, 40] # Navigation engine expert settings

CFG_PRT = [0x06, 0x00, 1] # Polls the configuration for one I/O port

CFG_PRT = [0x06, 0x00, 20] # Port configuration for UART ports

CFG_PRT = [0x06, 0x00, 20] # Port configuration for USB port

CFG_PRT = [0x06, 0x00, 20] # Port configuration for SPI port

CFG_PWR = [0x06, 0x57, 8] # Put receiver in a defined power state

CFG_RATE = [0x06, 0x08, 6] # Navigation/measurement rate settings

CFG_RINV = [0x06, 0x34, 1] # 1*N Get/set Contents of remote inventory

CFG_RST = [0x06, 0x04, 4] # Reset receiver / Clear backup data...

CFG_RXM = [0x06, 0x11, 2] # RXM configuration

CFG_RXM = [0x06, 0x11, 2] # RXM configuration

CFG_SBAS = [0x06, 0x16, 8] # SBAS configuration

CFG_TMODE2 = [0x06, 0x3D, 28] # Time mode settings 2

CFG_TMODE3 = [0x06, 0x71, 40] # Time mode settings 3

CFG_TP5 = [0x06, 0x31, 0] # Poll time pulse parameters for time...

CFG_TP5 = [0x06, 0x31, 1] # Poll time pulse parameters

CFG_TP5 = [0x06, 0x31, 32] # Time pulse parameters

CFG_TP5 = [0x06, 0x31, 32] # Time pulse parameters

CFG_USB = [0x06, 0x1B, 108] # USB configuration

ESF_INS = [0x10, 0x15, 36] # Vehicle dynamics information

ESF_MEAS = [0x10, 0x02, 8] # 4*numM...  Input/Output External sensor fusion measurements

ESF_RAW = [0x10, 0x03, 4] # 8*N Output Raw sensor measurements

ESF_STATUS = [0x10, 0x10, 16] # 4*numS...  Periodic/Polled External sensor fusion status

HNR_PVT = [0x28, 0x00, 72] # High rate output of PVT solution

INF_DEBUG = [0x04, 0x04, 0] # 1*N Output ASCII output with debug contents

INF_ERROR = [0x04, 0x00, 0] # 1*N Output ASCII output with error contents

INF_NOTICE = [0x04, 0x02, 0] # 1*N Output ASCII output with informational contents

INF_TEST = [0x04, 0x03, 0] # 1*N Output ASCII output with test contents

INF_WARNING = [0x04, 0x01, 0] # 1*N Output ASCII output with warning contents

LOG_BATCH = [0x21, 0x11, 100] # Batched data

LOG_ERASE = [0x21, 0x03, 0] # Erase logged data

LOG_FINDTIME = [0x21, 0x0E, 12] # Find index of a log entry based on a...

LOG_FINDTIME = [0x21, 0x0E, 8] # Response to FINDTIME request

LOG_INFO = [0x21, 0x08, 0] # Poll for log information

LOG_INFO = [0x21, 0x08, 48] # Log information

LOG_RETRIEVEBATCH = [0x21, 0x10, 4] # Request batch data

LOG_RETRIEVEPOSEXTRA = [0x21, 0x0f, 32] # Odometer log entry

LOG_RETRIEVEPOS = [0x21, 0x0b, 40] # Position fix log entry

LOG_RETRIEVESTRING = [0x21, 0x0d, 16] # 1*byteCo...  Output Byte string log entry

LOG_RETRIEVE = [0x21, 0x09, 12] # Request log data

MGA_ANO = [0x13, 0x20, 76] # Multiple GNSS AssistNow Offline...

MGA_BDS_EPH = [0x13, 0x03, 88] # BeiDou ephemeris assistance

MGA_BDS_ALM = [0x13, 0x03, 40] # BeiDou almanac assistance

MGA_BDS_HEALTH = [0x13, 0x03, 68] # BeiDou health assistance

MGA_BDS_UTC = [0x13, 0x03, 20] # BeiDou UTC assistance

MGA_BDS_IONO = [0x13, 0x03, 16] # BeiDou ionosphere assistance

MGA_DBD = [0x13, 0x80, 0] # Poll the navigation database

MGA_DBD = [0x13, 0x80, 12] # 1*N Input/Output Navigation database dump entry

MGA_FLASH_DATA = [0x13, 0x21, 6] # 1*size Input Transfer MGA_ANO data block to flash

MGA_FLASH_STOP = [0x13, 0x21, 2] # Finish flashing MGA_ANO data

MGA_FLASH_ACK = [0x13, 0x21, 6] # Acknowledge last FLASH_DATA or _STOP

MGA_GAL_ALM = [0x13, 0x02, 32] # Galileo almanac assistance

MGA_GAL_TIMEOFFSET = [0x13, 0x02, 12] # Galileo GPS time offset assistance

MGA_GAL_UTC = [0x13, 0x02, 20] # Galileo UTC assistance

MGA_GLO_EPH = [0x13, 0x06, 48] # GLONASS ephemeris assistance

MGA_GLO_ALM = [0x13, 0x06, 36] # GLONASS almanac assistance

MGA_GLO_TIMEOFFSET = [0x13, 0x06, 20] # GLONASS auxiliary time offset assistance

MGA_GPS_EPH = [0x13, 0x00, 68] # GPS ephemeris assistance

MGA_GPS_ALM = [0x13, 0x00, 36] # GPS almanac assistance

MON_TXBUF = [0x0A, 0x08, 28] # Transmitter buffer status

MON_VER = [0x0A, 0x04, 0] # Poll receiver and software version

MON_VER = [0x0A, 0x04, 40] # 30*N Polled Receiver and software version

NAV_AOPSTATUS = [0x01, 0x60, 16] # AssistNow Autonomous status

NAV_ATT = [0x01, 0x05, 32] # Attitude solution

NAV_CLOCK = [0x01, 0x22, 20] # Clock solution

NAV_DGPS = [0x01, 0x31, 16] # 12*numCh Periodic/Polled DGPS data used for NAV

NAV_HPPOSECEF = [0x01, 0x13, 28] # High precision position solution in ECEF

NAV_HPPOSLLH = [0x01, 0x14, 36] # High precision geodetic position solution

NAV_NMI = [0x01, 0x28, 16] # Navigation message cross_check...

NAV_ODO = [0x01, 0x09, 20] # Odometer solution

NAV_ORB = [0x01, 0x34, 8] # 6*numSv Periodic/Polled GNSS orbit database info

NAV_POSECEF = [0x01, 0x01, 20] # Position solution in ECEF

NAV_POSLLH = [0x01, 0x02, 28] # Geodetic position solution

NAV_PVT = [0x01, 0x07, 92] # Navigation position velocity time solution

NAV_RELPOSNED = [0x01, 0x3C, 40] # Relative positioning information in...

NAV_RESETODO = [0x01, 0x10, 0] # Reset odometer

NAV_SAT = [0x01, 0x35, 8] # 12*numSvs Periodic/Polled Satellite information

NAV_SLAS = [0x01, 0x42, 20] # 8*cnt Periodic/Polled QZSS L1S SLAS status data

NAV_SOL = [0x01, 0x06, 52] # Navigation solution information

NAV_STATUS = [0x01, 0x03, 16] # Receiver navigation status

NAV_SVINFO = [0x01, 0x30, 8] # 12*numCh Periodic/Polled Space vehicle information

NAV_SVIN = [0x01, 0x3B, 40] # Survey_in data

NAV_TIMEGLO = [0x01, 0x23, 20] # GLONASS time solution

NAV_TIMEGPS = [0x01, 0x20, 16] # GPS time solution

NAV_TIMELS = [0x01, 0x26, 24] # Leap second event information

NAV_TIMEUTC = [0x01, 0x21, 20] # UTC time solution

NAV_VELECEF = [0x01, 0x11, 20] # Velocity solution in ECEF

NAV_VELNED = [0x01, 0x12, 36] # Velocity solution in NED frame

RXM_MEASX = [0x02, 0x14, 44] # 24*num...  Periodic/Polled Satellite measurements for RRLP

RXM_PMREQ = [0x02, 0x41, 8] # Power management request

RXM_PMREQ = [0x02, 0x41, 16] # Power management request

RXM_RAWX = [0x02, 0x15, 16] # 32*num...  Periodic/Polled Multi_GNSS raw measurement data

RXM_RLM = [0x02, 0x59, 16] # Galileo SAR short_RLM report

RXM_RLM = [0x02, 0x59, 28] # Galileo SAR long_RLM report

RXM_RTCM = [0x02, 0x32, 8] # RTCM input status

RXM_SFRBX = [0x02, 0x13, 8] # 4*numW...  Output Broadcast navigation data subframe

RXM_SFRBX = [0x02, 0x13, 8] # 4*numW...  Output Broadcast navigation data subframe

RXM_SVSI = [0x02, 0x20, 8] # 6*numSV Periodic/Polled SV status info

TIM_HOC = [0x0D, 0x17, 8] # Host oscillator control

TIM_SMEAS = [0x0D, 0x13, 12] # 24*num...  Input/Output Source measurement

TIM_SVIN = [0x0D, 0x04, 28] # Survey_in data

TIM_TM2 = [0x0D, 0x03, 28] # Time mark data

TIM_TOS = [0x0D, 0x12, 56] # Time pulse time and frequency data

TIM_TP = [0x0D, 0x01, 16] # Time pulse time data

