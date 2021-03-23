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
          
 


          valid options to be picked up by this script are
           --install-base                   : Install base.
           --action                         : backup or restore 

           --output-dir                     : Output directory  



           options without a double-dash, will be passed on to the Standard Function to handle input options.

           N.B. Settings will only be applied if the appropriate value is set in the config file.
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
  typeset -r -g install_base=${__install_base:-}
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


  if [[ "${__test:-}" == "true" ]]
  then
    messageType="TEST"
  else
    messageType="INFO"
  fi
  LogMessage "${messageType}: Running with --install-base ${install_base} "
  LogMessage "${messageType}: Running with --action ${action} "
  LogMessage "${messageType}: Running with --archive-dir  is set to  ${archive_dir} "

  if [[ "${__test:-}" == "true" ]]; then exit 0 ; fi


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


BackupFolder() {

  ## Probably want to have a level above this..which decides whether to split into subfolders or not.
  ## Or maybe decide by size of folder?

  ## check if its got filesystems mounted on it... and warn/exit if it does , or split into separate filesystems?

  local folder_path="$1"  #The source folder you are backing up.
  local archive_path="$2"
  local additional_exclude_options=${3:-}

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
  

  

  ##temp 
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
  local relative_folder_path_as_line_separated=$( echo ${relative_folder_path} | sed 's!/!_!g' | sed 's/^_//' ) ## e.g change   /my/path to to my_path


  ## Name for top level, should just be the last part of top level
  base_top=$( basename ${top_level_path} )

 
  ## If it's not the top level call, then we need to add the top level path to here 
  if [[ "${top_level}"='true' ]]
  then 
    local archive_file_path=${archive_path}/${folder_name}.tar.z
  else
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
  tar --directory ${top_level_path}  ${exclude_options}  -cf ${archive_file_path} ${relative_folder_path}  ##--directory  = work from this directory; . backup from the directory you're working in. Means it gives relative path.
  vRC=$?
  LogMessage "tar of  ${folder_path} to  ${archive_file_path} finished with return code ${vRC} . "


  local counter=0 
  ## This is now backing up the things we excluded from original backup. ie. separate filesystems or objects that are greater than the split size.
  local filesystem 
  for filesystem in ${nested_filesystems[@]} ${objects_to_backup_separately[@]:-}
  #for filesystem in ${nested_filesystems[@]} 
  do
    counter=$(( counter + 1 ))

    if [[ "${filesystem}" =~ IISBackup ]]
    then
      LogMessage "INFO: Skipping ${filesystem} because it looks like IISBackup . "
      continue
    fi
    LogMessage "INFO: Doing tar of nested filesystem ${filesystem}"


    RunParallel() {
      local time_taken=$( TimeRun "BackupFolder ${filesystem} ${archive_dir}" )
      LogMessage "INFO: BackupFolder ${filesystem} ${archive_dir} took ${time_taken}"
    }

    RunParallel  & 

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



 
 
    

 