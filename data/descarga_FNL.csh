#!/usr/bin/env csh
# chmod 755 descarga_FNL.csh
# tcsh descarga_FNL.csh 20250315
#
# NOTE: if you want to run under a different shell, make sure you change
#       the 'set' commands according to your shell's syntax
# after you save the file, don't forget to make it executable
#   i.e. - "chmod 755 <name_of_script>"
#
# Experienced Wget Users: add additional command-line flags to 'opts' here
#   Use the -r (--recursive) option with care
#   Do NOT use the -b (--background) option - simultaneous file downloads
#       can cause your data access to be blocked
set opts = "-N"
#
# Check wget version.  Set the --no-check-certificate option 
# if wget version is 1.10 or higher
set v = `wget -V |grep 'GNU Wget ' | cut -d ' ' -f 3`
set a = `echo $v | cut -d '.' -f 1`
set b = `echo $v | cut -d '.' -f 2`
if(100 * $a + $b > 109) then
  set cert_opt = "--no-check-certificate"
else
  set cert_opt = ""
endif

# Validate input date in YYYYMMDD format
if($#argv < 1) then
  echo "Error: Debes proporcionar la fecha en formato YYYYMMDD"
  echo "Usage: $0 YYYYMMDD"
  exit 1
endif

set date = $1
set year  = `echo $date | cut -c1-4`
set month = `echo $date | cut -c5-6`
set day   = `echo $date | cut -c7-8`

set baseurl = "https://osdf-director.osg-htc.org/ncar/gdex/d083003/${year}/${year}${month}"

set filelist= ( \
  ${baseurl}/gdas1.fnl0p25.${date}00.f00.grib2 \
  ${baseurl}/gdas1.fnl0p25.${date}00.f03.grib2 \
  ${baseurl}/gdas1.fnl0p25.${date}00.f06.grib2 \
  ${baseurl}/gdas1.fnl0p25.${date}00.f09.grib2 \
)

while($#filelist > 0)
  set syscmd = "wget $cert_opt $opts $filelist[1]"
  echo "$syscmd ..."
  $syscmd
  shift filelist
end