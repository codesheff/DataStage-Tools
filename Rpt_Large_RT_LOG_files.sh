#!/bin/sh


vProject=dstage1
vProjectDir=/opt/IBM/InformationServer/Server/Projects/dstage1
vDSHOME=/opt/IBM/InformationServer/Server/DSEngine



###############################################################################################
vJobNoList=""
for vLine in $( du -ks ${vProjectDir}/RT_LOG* | sort -nr | head -10 |  tr '\t ' ',' )
do



 vSize=$( echo $vLine | cut -d, -f1 )
 vFile=$( echo $vLine | cut -d, -f2 )
 vJobNo=$( basename $vFile | sed 's/RT_LOG//' )

 vQuotedJobNo=$( echo "'"${vJobNo}"'" )


vJobNoList=$( echo ${vJobNoList},"'" ${vJobNo}"'")

## change to do single lookups for now...
cd ${vDSHOME} 1>/dev/null
echo " logto ${vProject}
select NAME FMT '40L', CATEGORY FMT '100L', JOBNO FROM DS_JOBS WHERE JOBNO = ${vQuotedJobNo}   ;
" | bin/uvsh 2>/dev/null | egrep 'Job name|No|Category'  | grep -v 'DSEngine logged on' |    awk -v awkSize=${vSize} 'BEGIN{ printf "size:" awkSize } { printf "," $0 } END{ print ""}'


cd - 1>/dev/null

done


###########################################################################################################

# This part is for when I get round to doing it as 1 select statement to get all jobs..vProjectDir
##

## remove initial comma
#vJobNoList=$( echo ${vJobNoList} | sed 's/^,//' | tr -d ' ' )
#echo ${vJobNoList}

#cd ${vDSHOME}


#echo " logto ${vProject}
#select NAME FMT '40L', CATEGORY FMT '100L', JOBNO FROM DS_JOBS WHERE JOBNO in ( ${vJobNoList} ) ;
#" | bin/uvsh


#cd -
