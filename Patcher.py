#!/usr/bin/python3
from pwn import *
import getpass
import time
from paramiko import AuthenticationException
from paramiko.ssh_exception import NoValidConnectionsError


class Patcher:
    def __init__(self,path,ist):
        try:
            self.binary = ELF(path)
            self.istructions = ist
            self.path = path
            self.name = self.CreateName()
            self.tryes = 0
        except FileNotFoundError:
            log.failure("The file doesn't exist ...")
            main()

        

    
    def Patch(self):

        if self.istructions == None:
            log.failure("Something goes wrong with your istructions... ; please insert them again!")
            self.istructions = GetIstructions(totOp)




        for op in self.istructions:
            self.binary.asm(op[0],op[1])


        self.binary.save(self.name)
        log.success(f"YOUR BINARY HAS BEEN PATCHED. YOU WILL FIND IT IN THE CURRENT DIRECTORY WITH THE FOLLOWING NAME --> {self.name}")
        if yesno("DO YOU WANT TO AUTOMATICALLY DO A RELEASE ON THE SERVER?",True) == True:
            self.Release()


        return True
    
    def CreateName(self):
        n = self.path.split('/')
        n = n[-1] + '_patched_' + str(time.strftime("%s",time.gmtime()))

        return n

    def Release(self):
        try:
            self.tryes +=1
            assert self.tryes <= 3
            creds=[]
            creds.append(input("[+] INSERT IP ADDRESS OF THE REMOTE MACHINE : ").rstrip("\n"))
            creds.append(input("[+] INSERT USERNAME : ").rstrip("\n"))
            creds.append(getpass.getpass("[+] INSERT PASSWORD : ").rstrip("\n"))
            s = ssh(user=creds[1],host=creds[0],password=creds[2])
            # soc = s.connect_remote(s.host,s.port)
            if s.connected()==False:
                raise ConnectionError

            remotePath = input("[+] INSTERT THE PATH OF THE REMOTE SERVICE : ").rstrip("\n")
            # service = remotePath.split("/")
            remoteService = input("[+] INSERT THE BINARY NAME : ").rstrip("\n")


         
            # s.upload_file(self.name)
            s.set_working_directory(remotePath.encode('utf-8'))
            s.upload_file(self.name)
            sh = s.shell()

           
            # move to service directory
            command = "cd " + remotePath
            sh.sendline(command)
            # rename the old binary with binary_old
            log.info("Renaming old binary ...")
            command = "mv " + remoteService + " " + remoteService +"_old"
            sh.sendline(command)
            #print(sh.recvrepeat(0.2))
            
            # rename the patched binary with the original binary name
            log.info("Applying the patch ...")
            command = "mv " + self.name + " " + remoteService 
            sh.sendline(command)
            #print(sh.recvrepeat(0.2))
            
            # make the binary executable
            log.info("Making the patched version executable ...")
            command = "chmod +x " + remoteService
            sh.sendline(command)
            #print(sh.recvrepeat(0.2))

            
            

            sh.close()
            s.close()
            # command = b"".join([b'mv ',remoteService,b' ',remoteService,b'_old'])
            # sh.sendline(command)
            # command= b"".join([b'mv ',self.name,b' ',remoteService])
            # sh.sendline(command)

            log.success("SUCCESS! The patched binary has been released. In case something goes wrong, you will find the original binary under the current name --> " + remoteService + "_old")
            


            


            

        except ConnectionError:
            log.critical("THE PROVIDED CREDENTIALS ARE WRONG!")
            if yesno("DO YOU WANT TO TRY AGAIN?",True) == True:
                self.tryes +=1
                self.Release()
            else:
                return False
        except socket.gaierror:
            log.critical("Invalid Host. Try again")
            self.tryes +=1
            self.Release()

        except AuthenticationException:
            log.critical("Unable to connect, try again!")
            self.tryes +=1
            self.Release()

        except NoValidConnectionsError:
            log.critical("Something goes wrong, try again!")
            self.tryes +=1
            self.Release()
            
        except AssertionError:
            log.critical("You tryed more than 3 times ... quitting ...")
            

        
        
        


def GetIstructions(num):
    try:
        Matrix = []
        for i in range(0,int(num)):
            log.info("ROW N° --> " + str(i+1))
            add = input("[>] INSERT THE ADDRESS:").rstrip('\n')
            if add.startswith("0x"):
                add= int(add,base=16)
            else:
                raise ValueError


            ist = input("[>] INSERT THE ISTRUCTION:").rstrip('\n')
            Matrix.append([])
            Matrix[i].append(add)
            Matrix[i].append(ist)
            print()

        return Matrix
    except ValueError:
        log.failure("ADDRES MUST BE ON FORM OF HEX NUMBER e.g 0x4000000")
        GetIstructions(totOp)



def main():
    try:
        global totOp
        
        
        print("")
        
        log.info_once('P4TcH3r v 1.0.0 @s0uNd_0f_s1l3nc3')
      
        
        path = input("[+] INSERT THE PATH OF THE BINARY : ").rstrip("\n")
        if os.path.exists(path)==False:
            raise FileNotFoundError

        if os.path.isfile(path) == False:
            raise IsADirectoryError
        
        totOp = input("[*] INSERT THE NUMBER OF ISTRUCTIONS YOU WANT TO MODIFY : ").rstrip('\n')
        print()
        lst = GetIstructions(totOp)
        p = Patcher(path,lst)
      

        p.Patch()
        
    except EOFError:
       if yesno("Are you sure you want to leave",False) == False:
           main()

    except KeyboardInterrupt:
        if yesno("Are you sure you want to leave",False) == False:
           main()
    
    except FileNotFoundError:
            log.failure("The file doesn't exist ...")
            main()

    except IsADirectoryError:
        log.failure("The provided string it's just a path, not a file")
        main()

    except TypeError:
        log.failure("Something goes wrong ... Try Again!")



if __name__=="__main__":
    main()