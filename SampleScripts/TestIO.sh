#!/bin/sh


smallFileSizeMeg=10  # in MB
bigFileSizeMeg=1000   # in MB
ParallelStreamsToRun=8
#smallFileSizeMeg=10  # in MB
#bigFileSizeMeg=200   # in MB
#ParallelStreamsToRun=5
largeFilsystemToRead=/ds/dt57/data/shared/ukdw
localTempFS=/dev/shm/SteTest
## create random file in memory

if [ ! -d  "${localTempFS}" ]
then
  mkdir ${localTempFS}
fi

chmod 775 ${localTempFS}

randomFile=${localTempFS}/random1
echo "Setting up random file in ${randomFile}" >&2
dd if=/dev/urandom    bs=1048576 count=${bigFileSizeMeg} of=${randomFile} 2>&1


# Get script name, without any of the path leading up to
scriptName="${0##*/}"

thisScriptDir=$( cd $(dirname $0) ; pwd; cd - >/dev/null)
vThisScriptDir=${thisScriptDir}

logFile="${thisScriptDir}/logs/remote_${logcmd}log_$(date +"%Y%m%d").txt"
logDateTime=$(date +"%Y%m%d_%H%M%S")
pid=$$
tempDir=${thisScriptDir}/tmp


echo "Hi,  you are running ${scriptName} in ${thisScriptDir}
I'm assuming that we want to write files to subdirectory in here. i.e ${tempDir}" >&2

if [ ! -d  "${tempDir}" ]
then
  mkdir ${tempDir}
fi
chmod 775 ${tempDir}

if [ ! -d  "${localTempFS}" ]
then
  mkdir ${localTempFS}
fi

chmod 775 ${localTempFS}



### Test 1  - du -hs

testDU() {
du -hs ${largeFilsystemToRead}/* >/dev/null 2>&1
##du -hs *
}


testFunction=testDU

#/usr/bin/time -o ./tmp/testFunction_time1.out -f "  real %e \t  user %U \t   sys %S" (testDU)
callTime() {

  
  funcToTest=$1
  TIMEFORMAT='real %3lR user %3lU sys %3lS'
  time ${funcToTest}
  
  # clear out temp dir
  rm ${tempDir}/*

}

funcToTest=testDU
callTime ${funcToTest} 2>&1 | awk -v Func=${funcToTest} '{print Func": " $0 }'

testWriteFilesInParallel() {
  size=$1
  iNumToRun=$2
  WriteFile() {
       vUniqueFile=${tempDir}/testout_$(hostname)_$$_${iCounter}.out
##       WriteSpeed=$(dd if=/dev/urandom bs=1048576 count=${bigFileSizeMeg} of=${vUniqueFile} 2>&1 |
       WriteSpeed=$(dd if=${randomFile}    bs=1048576 count=${bigFileSizeMeg} of=${vUniqueFile} 2>&1 |
              grep copied | cut -d"," -f 3)
                 echo WriteSpeed stream ${iCounter} $WriteSpeed
         }
  iCounter=1
  while [ "${iCounter}" -le ${iNumToRun} ]
  do
     WriteFile & ## do in background so we can test parallel
     iCounter=$(( $iCounter + 1 ))
  done
  wait
}

funcToTest="testWriteFilesInParallel ${bigFileSizeMeg} ${ParallelStreamsToRun}"
callTime "${funcToTest}" 2>&1 | awk -v Func="${funcToTest}" '{print Func": " $0 }'

### Additional tests to add
##  These might be done as separate script though, as requires 2 servers and is more compex testing
## 1. SCP file from headnode to nfs server - to disk...and to /dev/null
## 2. SCP file from nfs      to headnode   - to disk...and to /dev/null
##  Should tell us if there's a difference between nfs  and just network ( scp)
## 
