const { exec, spawn } = require('child_process');
const logger = require('./logger')
const path = require('path')

const ADB_PORT = 5037;
const ADB_NAME = "adb.exe";
const KILL_PROCESS_PS_PATH = path.resolve(__dirname, '..', 'scripts', 'kill_process.ps1');

// Function to fetch the PID of the process listening on the specified port
const findProcessUsingPort = (port) => {
  return new Promise((resolve, reject) => {
    const command = process.platform === 'win32' ? `netstat -ano | findstr :${port}` : `lsof -i :${port}`;

    logger.info(`Finding process using port ${port} ...`);
    exec(command, (error, stdout, stderr) => {
      if (error) {
        return reject(error);
      }

      const lines = stdout.split('\n').filter(line => line.trim() !== '').map(line => line.trim());
      if (process.platform === 'win32') {
        if (lines.length > 0) {
          const line = lines.find(line => line.toUpperCase().includes('LISTENING'));
          if(!line) {
            return resolve(null)
          }
          // For Windows, the PID is in the last column (index 4)
          const pid = line.split(/\s+/)[4]
          return resolve(Number(pid));
        } else {
          return resolve(null);
        }
      } else {
        if (lines.length > 1) {
          // For macOS and Linux, the PID is in the second column (index 1)
          const pid = lines[1].split(/\s+/)[1]
          return resolve(Number(pid));
        } else {
          return resolve(null);
        }
      }
    });
  });
};

// Function to kill the process using the given PID
const killProcess = (pid) => {
  return new Promise((resolve, reject) => {
    if (!pid) {
      return resolve();
    }

    const killCommand = process.platform === 'win32' ? `taskkill /PID ${pid} /F` : `kill ${pid}`;

    exec(killCommand, (error, stdout, stderr) => {
      if (error) {
        return reject(error);
      }

      return resolve();
    });
  });
};

// Function to kill the process using the given PID with powershell
const killProcessPS = async (pid, pname) => {
  return new Promise((resolve, reject) => {
    if (process.platform !== 'win32') {
      return resolve();
    }
    
    const command = 'powershell.exe';
    const args = ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', KILL_PROCESS_PS_PATH, pid ? pid : "", pname];

    const child = spawn(command, args);

    child.stdout.on('data', (data) => {
      logger.info(`PowerShell Script Output: ${data}`);
    });

    child.stderr.on('data', (data) => {
      logger.error(`${new Date().toISOString()}: Error: ${data}`);
      reject(`${new Date().toISOString()}: Error: ${data}`)
    });

    child.on('close', (code) => {
      logger.info(`Child process exited with code ${code}`);
      if(code === 0) {
        resolve()
      } else {
        reject(new Error(`Child process exited with code ${code}`))
      }
    });
  });
};

const relaunchADB = () => {
  return new Promise((resolve, reject) => {
    logger.info(`Doing adb start-server ...`);

    exec(`adb start-server`, (error, stdout, stderr) => {
      if (error) {
        return reject(error);
      }
      exec(`adb devices`, (error, stdout, stderr) => {
        if (error) {
          return reject(error);
        }
        logger.info(stdout)
        return resolve();
      });
    });
  });
};

const redeploySTFProxy = () => {
  return new Promise((resolve, reject) => {
    logger.info(`Redeploying stf-proxy...`);
    exec(`pm2 restart "stf proxy"`, (error, stdout, stderr) => {
      if (error) {
        return reject(error);
      }
      logger.info(stdout)
      return resolve();
    });
  });
};

const redeployTMDC = () => {
  return new Promise((resolve, reject) => {
    logger.info(`Redeploying TMDC...`);
    exec(process.platform === 'win32' ? `wsl cd; .nvm/versions/node/v8.16.1/bin/pm2 restart all` : "pm2 restart all", (error, stdout, stderr) => {
      if (error) {
        return reject(error);
      }
      logger.info(stdout)
      return resolve();
    });
  });
};

// Restart the process after killing it
const restartAll = async () => {
  try {
    const pid = await findProcessUsingPort(ADB_PORT);
    logger.info(`ADB PID is ${pid}`);

    await killProcessPS(pid, ADB_NAME)
    logger.info(`Process ${ADB_NAME} with PID ${pid} killed.`);

    await relaunchADB()
    try {
      await redeploySTFProxy()
    } catch (err) {
      logger.error(`${new Date().toISOString()}: Could not redeploy stf-proxy: ${err}`);
    }
    await redeployTMDC()

    logger.info("ADB failsafe routine done!")
  } catch (err) {
    logger.error(`${new Date().toISOString()}: Error occurred: ${err}`);
  }
};

const solveAddressInUse = async (port) => {
  try {
    const pid = await findProcessUsingPort(port);
    logger.info(`PID using :${port} is ${pid}`);

    await killProcess(pid);
    logger.info(`Process with PID ${pid} killed.`);
  } catch (err) {
    logger.error(`${new Date().toISOString()}: Error occurred: ${err}`);
  }
}

// Call the restartProcess function
module.exports = {
  restartAll: restartAll,
  solveAddressInUse: solveAddressInUse
}