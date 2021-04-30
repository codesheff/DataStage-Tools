#!/bin/bash

set -u  ## Error if variables are used without being defined first

#set -x 
#Do not use Hungarian notation 
#Do not use a prefix for member variables (_, m_, s_, etc.). If you want to distinguish between local and member variables you should use 'this. in C# and 'Me.' in VB.NET. 
#Do use camelCasing for member variables 
#Do use camelCasing for parameters 
#Do use camelCasing for local variables 
#Do use PascalCasing for function, property, event, and class names 
#Do prefix interfaces names with 'I' 
#Do not prefix enums, classes, or delegates with any letter 





SetupInputOptions() {
## Setup inputOptionsArray
## This will be accessible to other functions called by this script
  inputOptions=()
  inputOptions+=('')  ## Need at least one entry in array to avoid 'Unbound variable' error
  for option in "$@"
  do
    #echo handle option $option
    inputOptions+=("$option")
  done
}

Local_HandleInputOptions() {


  usage() {

    

    echo "

         This script is for backup and restore of data on a path ( --install-base)

         For backup:
           This script performs backup of a path ( --install-base).
           It will creaate separate tar file for any filesystem under that path.
           It will also split large directories into smaller tar files.
          
 


          valid options to be picked up by this script are
           --install-base                   : Install base.
           --action                         : backup or restore 

           --output-dir                     : Output directory  
           [--max-parallel <value> ]         : Maximum parallel backups to run. Defaults to number of cpus/2  


         "
  }


  ## Check original shell option
  orig_options_for_u=${-//[^u]/}
  set +u


  ## elements in array
  paramCount=${#inputOptions[@]}
  for ((i = 0 ; i < ${paramCount} ; i++));
  do
    case ${inputOptions[${i}]} in
        --install-base)
                                ## This is an example of an option that has a value
                                install_base_supplied='TRUE'
                                typeset  __install_base                           ## Create the variable
                                SetVariableFromInputOptionValue __install_base     ## Set variables value in using the function
                                typeset  -r __install_base                         ## Set it as read only ( keeping the value )
                                ;;
        --action)
                                ## This is an example of an option that has a value
                                typeset  __action                                 ## Create the variable
                                SetVariableFromInputOptionValue __action           ## Set variables value in using the function
                                typeset  -r __action                               ## Set it as read only ( keeping the value )
                                ;;

        --archive-dir)
                                ## This is an example of an option that has a value
                                typeset  __archive_dir                                 ## Create the variable
                                SetVariableFromInputOptionValue __archive_dir           ## Set variables value in using the function
                                typeset  -r __archive_dir                          ## Set it as read only ( keeping the value )
                                ;;

        --max-parallel)
                                ## This is an example of an option that has a value
                                typeset  __max_parallel                                 ## Create the variable
                                SetVariableFromInputOptionValue __max_parallel           ## Set variables value in using the function
                                typeset  -r __max_parallel                          ## Set it as read only ( keeping the value )
                                ;;

        --test)
                                inputOptions[${i}]='' # remove input option once it is handled here
                                typeset -r  __test='true'
                                ;;




        -h | --help )           usage
                                exit
                                ;;
        --*)                    LogMessage "ERROR: unhandled --parameter ${inputOptions[${i}]}"
                                usage
                                exit
                                ;;
                  *)            continue;; ## allow unhandled options to remain. They will be checked by the standard function HandleInputOptions()
    esac
  done



  if [[ "${orig_options_for_u}" == "u" ]]
  then
    set -u
  fi


# This script will use the shared functions to do the full end to end install of DataStage 
  
  typeset -r -g install_base=$( echo "${__install_base:-}" | sed 's!/\s*$!!' )  ## remove any trailing '/' 
  if [[ ( ! -z ${install_base} ) && -d  ${install_base}  ]]
  then 
    LogMessage "INFO: --install-base ${install_base} is valid and exists."
  else
    LogMessage "ERROR: --install-base ${install_base} is not valid."
    usage
    exit 9
  fi

  typeset -r -g action=${__action:-}
  if [[ ( "${action}" == "backup" ) || ( "${action}" == "restore" )  ]]
  then 
    LogMessage "INFO: --action ${action} is valid."
  else
    LogMessage "ERROR: --action ${action} is not valid."
    usage
    exit 9
  fi

  typeset -r -g archive_dir=${__archive_dir:-}
  if [[ ( ! -z ${archive_dir} ) && -d  ${archive_dir}  ]]
  then
    LogMessage "INFO: --archive-dir ${archive_dir} is valid and exists."
  else
    LogMessage "ERROR: --archive-dir ${archive_dir} is not valid. It must be supplied and it must exist."
    usage
    exit 9
  fi

  local number_of_processors=$( grep -c ^processor /proc/cpuinfo ) 
  local our_recommended_max_limit=${number_of_processors}  ## just a guess..not really tested.
  local default_max_parallel=$(( ${number_of_processors}/ 2 ))  ## just a guess..not really tested.

  local temp_max_parallel=${__max_parallel:-${default_max_parallel}}
  if [[ "${temp_max_parallel}" -ge ${our_recommended_max_limit} ]]
  then
    LogMessage "INFO: --max-parallel was provided as  ${temp_max_parallel}, but we're limiting it to ${our_recommended_max_limit} on this environment, as it has ${number_of_processors} processors available ."
    temp_max_parallel=${our_recommended_max_limit}
  fi
  typeset -g -r max_parallel=${temp_max_parallel}

  


  if [[ "${__test:-}" == "true" ]]
  then
    messageType="TEST"
  else
    messageType="INFO"
  fi
  LogMessage "${messageType}: Running with --install-base ${install_base} "
  LogMessage "${messageType}: Running with --action ${action} "
  LogMessage "${messageType}: Running with --archive-dir  is set to  ${archive_dir} "
  LogMessage "${messageType}: Running with --max-parallel is set to  ${max_parallel} "

  if [[ "${__test:-}" == "true" ]]; then exit 0 ; fi


}


#### Already shared

#!/bin/bash


SetupLog() {
  typeset -g thisScriptDir=$( cd $(dirname $0) ; pwd; cd - >/dev/null)
  typeset -g thisScript=$(basename $0)

  
  ## If logFile is already set, continue using same value:

  if [[ -z "${logFile:-}" ]]
  then

    vTimeStamp=`date '+%Y%m%d_%H%M%S'`

    # Create log files directory
    logFileDir=/tmp/Logs_$(whoami)_$(date '+%Y%m%d')

    if [[ ! -e ${logFileDir} ]] 
    then 
      mkdir ${logFileDir}
    fi

    chmod 775 ${logFileDir}

    logFileBaseName=${thisScript}
    logFileName=${logFileBaseName}_${vTimeStamp}.log
    typeset -g logFile=${logFileDir}/${logFileName}

    >${logFile}
    chmod 755 ${logFile}
    tmpERR=/${logFileDir}/tmpERR-$$
    >${tmpERR}
    chmod 755 ${tmpERR}

  fi

  LogMessage "INFO: Log messages will be written to ${logFile}"

  
}

LogMessage () {

  logDate=`date '+%y/%m/%d %H:%M:%S'`
  message="$1"
  message_plus="${message} - ( Message from ${FUNCNAME[@]} - Script name : $0 )"  ## Could build this up by looping through the FUNCNAME array to get full list of functions.

  if [ -z "${logFile}" ]
  then 
    echo "[ ${logDate} ] - ${message_plus} " >&2
  else
    logDate=`date '+%y/%m/%d %H:%M:%S'`
    echo "[ ${logDate} ] - ${message_plus}"  | tee -a ${logFile} >&2
  fi
}


SetVariableFromInputOptionValue(){

  ## This fuction will work on the inputOptions options array that is already set up in the calling function
  ##   and uses the value of i controlled in the calling function


  if [[ -z "${inputOptions[@]:-}" ]]
  then
    LogMessage "ERROR: inputOptions array does not exist"
    return 9
  #else
  #  LogMessage "INFO : inputOptions array is "${inputOptions[@]}
  fi


  variable_to_set=$1


  optName="${inputOptions[${i}]}"
  inputOptions[${i}]='' # remove input option once it is handled here
  i=$(( i + 1 )) ##i++ # move to next entry, which is the value

  ## code to handle empty value being passed
  typeset  tmp=${inputOptions[${i}]-}
  if [[ "${tmp}" =~ ^- ]]
  then
    ##invalid value supplied
    LogMessage "INFO: Assuming that ${optName}  is being passed as empty. Value can not start with '-'"
    tmp=""
    i=$(( i - 1 ))  ## go back , to this can be processed again as a new -- variable
  else
    ##value supplied is ok
    ## keep 'tmp' as it is
    inputOptions[${i}]='' # remove input option once it is handled here
  fi

  ## Set variable to contents of 'tmp'
  eval "${variable_to_set}+=(\"${tmp}\")"   ## Treat it like an array. Works for simple strings too. ( just initialise variable before calling this function ) 


}



################### MOVE TO SHARED ??


CreateDir() {
  typeset targetDirectory=$1

   LogMessage "INFO: Creating dir ${targetDirectory}"

  # Make sure taraget directory exists
  if [[ ! -d ${targetDirectory} ]]
  then
    orig_umask=$(umask)
    umask 022
    mkdir -p ${targetDirectory}
    umask ${orig_umask}
  fi
}

TimeRun(){
 ##  Capture time taken to run something. ( Why  is this so fiddly?)

  local command="${1}"

  # Keep both stdout and stderr unmolested.
  # http://mywiki.wooledge.org/BashFAQ/032
  # The shell's original FD 1 is saved in FD 3, which is inherited by the subshell.
  # Inside the innermost block, we send the time command's stdout to FD 3.
  # Inside the innermost block, we send the time command's stderr to FD 4.
  exec 3>&1 4>&2
  local time_output=$( { time ${command}  1>&3 2>&4; } 2>&1 )  # Captures time only.
  exec 3>&- 4>&-

  real_time=$( echo -e  "${time_output}"  | grep real | sed 's/real//' | tr -d '\t' | tr -s ' ' ) 


  echo "${real_time}"


}

BackupFolder(){

  local folder_path="$1"  #The source folder you are backing up.
  local archive_path="$2"
  local additional_exclude_options=${3:-}


  ## Create a file to be the temp tar script.
  local temp_script_file=$(  mktemp --tmpdir=/localwork2/temp ds_backup_tar_commands.XXX.tmp )

  GenerateTarScript "${folder_path}" "${archive_path}"  "${temp_script_file}"
  vRC=$?

  LogMessage "INFO: tar script created at ${temp_script_file}"

  LogMessage "INFO: running tar commands."
  OLDIFS="$IFS"
  IFS=$'\n'

  ok_to_continue='false'

























































  number_of_commands_to_run=$( cat  ${temp_script_file} | sort | uniq | wc -l ) 
  LogMessage "INFO: About to run ${number_of_commands_to_run} tar commands."
  return_code_array=()

  counter=0
  for tar_command in $( cat  ${temp_script_file} | sort | uniq  )
  do
    while [[ "${ok_to_continue}" == 'false' ]]
    do
      counter=$(( counter + 1 ))
      #number_of_background_jobs=$(( $( jobs | wc -l ) -1 ))  # take one off, as you always need one background proceses just to be in here.
      number_of_background_jobs=$( jobs | wc -l )
      #number_of_background_jobs=$( pstree -aup ${current_pid} | grep ' tar ' | grep -v grep | wc -l )

      if [[ ${number_of_background_jobs} -ge ${max_parallel} ]]
      then
        LogMessage "DEBUG: Already have  ${number_of_background_jobs} background jobs running, so sleep for 10s and check again."
        local current_jobs=$( jobs )
        LogMessage "DEBUG: Shown current jobs. ${current_jobs} "
        ## sleep 10 seconds and then test again
        sleep 10
        #LogMessage "DEBUG: current pid is ${current_pid} "
        #pstree -aup ${current_pid}

        continue
      else
        LogMessage "DEBUG: Currrent number of background jobs is number_of_background_jobs is ${number_of_background_jobs}. ok to continue  "
        ok_to_continue='true'
        break
      fi
    done

    # Run the tar command 
    {
      ${tar_command}
      vRC=$?
      return_code_array[${counter}]=${vRC}
    }
    
  done

  IFS="$OLDIFS"

  ## Check through return code array
  counter=0
  for return_code in "${return_code_array[@]}"
  do
    counter=$(( counter + 1 ))
    LogMessage "INFO: return code for command ${counter} : ${return_code}"
  done


  


}

GenerateTarScript() {

  ## Probably want to have a level above this..which decides whether to split into subfolders or not.
  ## Or maybe decide by size of folder?

  ## check if its got filesystems mounted on it... and warn/exit if it does , or split into separate filesystems?

  local folder_path="$1"  #The source folder you are backing up.
  local archive_path="$2"
  local temp_script_file=${3}

  local split_size_bytes=500000000

  #for funcname in "${FUNCNAME[@]}"
  #do
  #  LogMessage "TEMP: funcname ${funcname}"
  #done  
  if [[ "${install_base}" == "${folder_path}" ]]
  then
    local top_level='true'
    typeset -g top_level_path=${folder_path}
    LogMessage "INFO: This is the top level call to BackupFolder . Top level path is ${top_level_path}"
  else
    local top_level='false'
    LogMessage "INFO: This is a recursive call to BackupFolder . Top level path is ${top_level_path} "
    
    ## Need to remember to add the original part to the name of the archive file.
   
  fi
  

  

  local additional_exclude_options=" --exclude=${folder_path}/IISBackup "  ## allows you to backup /iis/dtxx without IISBackup

  local folder_size_bytes
  local folder_size_bytes=$( du -s -b "${folder_path}"  | cut -f 1 )

  ## Maybe put some logic in here.. to say if certain size, then do each subfolder  as separate backup.
  ##  ie add it to the exclude options and the list of additional things to process, like you do with fs.

  local objects_to_backup_separately=()  ## use this array to store names of objects that we exclude from this backup, and then backup separately.
  if [[ ${folder_size_bytes} -ge ${split_size_bytes} ]]
  then
    LogMessage "INFO: Folder size is greater than split size."
    ## Checking for subfolders or files
    
    local folder_name
    local folder_size
    for object_size in $( du -bs ${folder_path}/* | sed 's/\t/~/' )
    do
      folder_name=$( echo ${object_size}  | cut -d '~' -f 2 )
      folder_size=$( echo ${object_size}  | cut -d '~' -f 1 )
      #LogMessage "INFO: ${folder_name} ${folder_size} "

      ## If any individual object in this dir is greater than the split size, then back that up separately.
      if [[ ${folder_size} -ge ${split_size_bytes} ]]
      then
        LogMessage "INFO: ${folder_name} is larger than the split size, so will be backed up separately."
        objects_to_backup_separately+=(${folder_name})
      fi

    done 

  else
    LogMessage "INFO: Folder size ( ${folder_size_bytes} ) is less than split size ( ${split_size_bytes} )."



  fi



  LogMessage "INFO: Backup up ${folder_path} to ${archive_path}"
  LogMessage "INFO: ${folder_path} has size ${folder_size_bytes} (bytes)."

  LogMessage "TEMP: running  df -hP | grep \" ${folder_path}/\" |   awk '{print \$NF}' " 

  ## Checking if any filesytems are mounted under this location
  ## Any nested filesystems should be excluded from this backup, and then backed up explicitly
  local nested_filesystems=$( df -hP | grep " ${folder_path}/" |   awk '{print $NF}' )
  LogMessage "INFO: Filesytems found under this location. ${nested_filesystems}"


  local exclude_options=" --exclude=./.snapshot " 
  exclude_options+=" --exclude=./IISBackup "

  ## build up exclude options for filesystems and objects we are backing up separately. 
  LogMessage "DEBUG:  ${objects_to_backup_separately[@]:-Nothing in objects}  when backing up ${folder_path} "
  for filesystem in ${nested_filesystems[@]} ${objects_to_backup_separately[@]:-}
  do
    ## Need to exclude the path of the filesystem relative to where we're backing up.
    ## If backing up from /iis/dt7g  and  you want to exclude /iis/dt7g/IISBackup , then  --exclude=./IISBackup 
    ##   So for the filestem paths, we want to replace the /iis/dt7g/ with './'
    local path_to_exclude=$( echo ${filesystem} | sed "s!${folder_path}/!./!" )

    LogMessage "TEMP: path_to_exclude is ${path_to_exclude}.   filesystem ${filesystem}  folder path ${folder_path} "
    exclude_options+=" --exclude=${path_to_exclude}"
  done





  local folder_name=$( basename ${folder_path}  )
  local relative_folder_path=$( echo  ${folder_path}  |  sed "s!${top_level_path}!.!" ) 
  #local relative_folder_path_as_line_separated=$( echo ${relative_folder_path} | sed 's!/!_!g' |  sed 's/^.//'  | sed 's/^_//'  ) ## e.g change   /my/path to to my_path
  LogMessage "TEMP: relative_folder_path is ${relative_folder_path}"
  local relative_folder_path_as_line_separated=$( echo ${relative_folder_path} |  sed 's!^./!!' |  sed 's!/!_!g'  ) ## e.g change   /my/path to to my_path


  ## Name for top level, should just be the last part of top level
  base_top=$( basename ${top_level_path} )

 
  ## If it's not the top level call, then we need to add the top level path to here 
  if [[ "${top_level}" == 'true' ]]
  then 
    LogMessage "DEBUG: This is top level, so no need to add base name to archive file path. ${install_base} matches ${folder_path}  "
    LogMessage "DEBUG: top_level is ${top_level}  "
    local archive_file_path=${archive_path}/${folder_name}.tar.z
  else
    LogMessage "DEBUG: This is recursive call, so base name added  to archive file path.  ${install_base} does not match ${folder_path} "
    LogMessage "DEBUG: top_level is ${top_level}  "
    local archive_file_path=${archive_path}/${base_top}_${relative_folder_path_as_line_separated}.tar.z
  fi

  CreateDir "${archive_path}"

  if [[ -e ${archive_file_path} ]]
  then
    local backup=${archive_file_path}_$(date +'%Y%m%d_%H%M%S')_$$
    LogMessage "INFO: Moving existing archive at ${archive_file_path} to ${backup}"
    mv ${archive_file_path}  ${backup}
  fi

  LogMessage "INFO: Starting tar command" 
  LogMessage "DEBUG: Running tar --directory ${top_level_path} --gzip  ${exclude_options}  -cf ${archive_file_path} ${relative_folder_path}"  ##--directory  = work from this directory; . backup from the directory you're working in. Means it gives relative path.

  #tar --directory ${top_level_path} --gzip  ${exclude_options}  -cf ${archive_file_path} ${relative_folder_path}   ##--directory  = work from this directory; . backup from the directory you're working in. Means it gives relative path.
  echo "tar --directory ${top_level_path} --gzip  ${exclude_options}  -cf ${archive_file_path} ${relative_folder_path} \# "  >> ${temp_script_file}  ##--directory  = work from this directory; . backup from the directory you're working in. Means it gives relative path.


  local counter=0 
  ## This is now backing up the things we excluded from original backup. ie. separate filesystems or objects that are greater than the split size.
  local filesystem 

  ## remove duplicates across the two arrays
  OLDIFS="$IFS"
  IFS=$'\n'
  combined_object_list=(`for R in "${nested_filesystems[@]:-}" "${objects_to_backup_separately[@]:-}" ; do echo "$R" ; done | sort -du`)

  ## TEMP###
  ## temp output list to file
  tempfile=$(  mktemp --tmpdir=/localwork2/temp ds_backup.XXX.tmp )
  for line in "${combined_object_list[@]:-}"
  do
    echo "${line}" >>  ${tempfile}

  done



  ###
  IFS="$OLDIFS"
  #for filesystem in ${nested_filesystems[@]} ${objects_to_backup_separately[@]:-}

  LogMessage "                                                                                            "
  LogMessage "                                                                                            "
  LogMessage "                                                                                            "
  LogMessage "                                                                                            "
  LogMessage "                                                                                            "
  LogMessage "INFO: This call to BackupFolder should create ${#combined_object_list[@]:-} background jobs."

  for filesystem in ${combined_object_list[@]:-} 
  do
    counter=$(( counter + 1 ))

    if [[ "${filesystem}" =~ IISBackup ]]
    then
      LogMessage "INFO: Skipping ${filesystem} because it looks like IISBackup . "
      continue
    fi
    LogMessage "INFO: Doing tar of nested filesystem ${filesystem}"

    ok_to_continue='false'
    #number_of_tar_commands_running=$( pstree -aup | grep ' tar ' | wc -l ) 
    
    # using number of tar commands instead of number of jobs
    #number_of_background_jobs=${number_of_tar_commands_running}
    ## nb 
    current_pid=$$
    LogMessage "DEBUG: current pid is ${current_pid} "
    while [[ "${ok_to_continue}" == 'false' ]]
    do
      #number_of_background_jobs=$(( $( jobs | wc -l ) -1 ))  # take one off, as you always need one background proceses just to be in here.
      #number_of_background_jobs=$( jobs | wc -l )                                                                                     
      number_of_background_jobs=$( pstree -aup ${current_pid} | grep ' tar ' | grep -v grep | wc -l ) 

      if [[ ${number_of_background_jobs} -ge ${max_parallel} ]]   
      then
        LogMessage "DEBUG: Already have  ${number_of_background_jobs} background jobs running, so sleep for 10s and check again."
        local current_jobs=$( jobs ) 
        LogMessage "DEBUG: Shown current jobs. ${current_jobs} "
        ## sleep 10 seconds and then test again
        sleep 10
        #LogMessage "DEBUG: current pid is ${current_pid} "
        pstree -aup ${current_pid}
       
        continue
      else
        LogMessage "DEBUG: Currrent number of background jobs is number_of_background_jobs is ${number_of_background_jobs}. ok to continue  "
        ok_to_continue='true'
        break 
      fi
    done
    


    #RunParallel() {
    #  local time_taken=$( TimeRun "BackupFolder ${filesystem} ${archive_dir}" )
    #  LogMessage "INFO: BackupFolder ${filesystem} ${archive_dir} took ${time_taken}"
    #}

    

    #RunParallel   & 
    {
      #local time_taken=$( TimeRun "BackupFolder ${filesystem} ${archive_dir}" )
      local time_taken=$( TimeRun "GenerateTarScript ${filesystem} ${archive_dir} ${temp_script_file}" )
      LogMessage "INFO: BackupFolder ${filesystem} ${archive_dir} took ${time_taken}"
    } &  ## run this in background to allow parallel running.

    number_of_background_jobs=$( jobs | wc -l ) 
    LogMessage "INFO: Number of backgound jobs running is ${number_of_background_jobs} ."

    LogMessage "INFO: Counter is ${counter} ."
    #if [[ ${counter} -ge 3 ]]
    #then 
    #  break 
    #fi


  done

  LogMessage "INFO: Waiting for parallel backups to complete"
  wait








}



########################

#### MAIN PROGRAM #########

thisScriptDir=$( cd $(dirname $0) ; pwd; cd - >/dev/null)

typeset -i error_count=0

## Standard Functions are in the SubScripts directory
. ${thisScriptDir}/StandardFunctions.env

SetupLog;
echo logfile is ${logFile}
LogMessage "INFO: Detailed Log file is ${logFile}"

SetupInputOptions  "$@"
Local_HandleInputOptions ${inputOptions}              ;vRC=$?; if [ ${vRC} -ne 0 ] ; then LogMessage "Installation abandoned with rc=${vRC}"; funcTidyUp; exit 3; fi

cat /dev/null > /localwork2/stetempscript.sh
case ${action} in 
  backup)
    time_taken=$( TimeRun "BackupFolder ${install_base} ${archive_dir}"; vRC=$? ) 
    LogMessage "INFO: Total backup time taken :  ${time_taken}"
    LogMessage "INFO: BackupFileSystems finished with return code ${vRC} ."
    ;;
  restore)
    LogMessage "INFO: Not coded yet."
    ;;
  *) 
    LogMessage "ERROR: Invalid action ${action}"
    ;;
esac


LogMessage "INFO: Detailed Log file is ${logFile}"
LogMessage "INFO: End of Script."



 
 
    

 
