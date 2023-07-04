const os = require('os')
const path = require('path')
const fs = require('fs')
const { exec } = require('child_process')

const Win = require('windows-interact')
const robot = require("robotjs");

const config = require('./config')

const QPM_PROCESS_NAME = "QualcommPackageManager.exe"
const QUTS_PROCESS_NAME = "QUTSService.exe"

try {

  Win.set.preferences({
    appManagerRefreshInterval: 2500,
    // Log options
    log: {
      // File to save log and error history
      outputFile: `${os.homedir()}\\logs`,
      // Show or hide timestamp in log (For Win.log & Win.error)
      showTime: true,
      // Control verbosity of parts of windows-interact
      verbose: {
        // Show preformatted log when requests are made
        requestTo: true,
        // Be verbose while managing PowerShell sessions
        appManager: true
      }
    }
  })

  const isRunning = (appName, processName) => {
    return new Promise((resolve) => {
      Win.process.isRunning(processName, function (isRunning) {
        const withAppManager = Object.keys(Win.appManager.registeredApps).includes(appName) && Win.appManager.registeredApps[appName].isRunning === true
        resolve(isRunning || withAppManager)
      })
    }, (reject) => {
      reject(false)
    })
  }

  const isLoggedIn = async () => {
    return new Promise((resolve) => {
      Win.process.getWindowTitle(QPM_PROCESS_NAME, function (windowTitle) {
        resolve(typeof windowTitle == 'string')
      })
    }, (reject) => {
      reject(false)
    })
  }

  const findQpmPath = function () {
    if (config.QUALCOMM_PATH) {
      return path.join(config.QUALCOMM_PATH, 'QPM', QPM_PROCESS_NAME)
    }

    const defaultBasePath = fs.existsSync(Win.path`C:\Program Files (x86)\Qualcomm\QPM`) ? Win.path`C:\Program Files (x86)\Qualcomm\QPM` : Win.path`C:\Program Files\Qualcomm\QPM`
    if (!fs.existsSync(defaultBasePath)) {
      throw new Error(`QPM path not provided through config and does not exist in the default path ${defaultBasePath}`)
    }

    // use latest version
    const dirs = fs.readdirSync(defaultBasePath, { withFileTypes: true }).filter(dir => dir.isDirectory()).map(dir => dir.name)
    dirs.sort().reverse()
    console.log("QPM versions", dirs)
    const latest = dirs[0]
    console.log("Using latest version", latest)

    const qpmPath = path.join(defaultBasePath, latest, QPM_PROCESS_NAME)
    // final format of path to remove extra characters
    const formattedPath = String.raw`${qpmPath}`.replace(new RegExp('\\'.replace(/([.*+?^=!:${}()|\[\]\/\\\r\n\t|\n|\r\t])/g, '\\$1'), 'g'), '\\\\')
    console.log("QPM path", formattedPath)
    return formattedPath
  }

  const findQutsPath = function () {
    if (config.QUALCOMM_PATH) {
      return path.join(config.QUALCOMM_PATH, 'QPM', QUTS_PROCESS_NAME)
    }

    const defaultBasePath = fs.existsSync(Win.path`C:\Program Files (x86)\Qualcomm\QUTS`) ? Win.path`C:\Program Files (x86)\Qualcomm\QUTS` : Win.path`C:\Program Files\Qualcomm\QPM`
    if (!fs.existsSync(defaultBasePath)) {
      throw new Error(`QUTS path not provided through config and does not exist in the default path ${defaultBasePath}`)
    }

    const qutsPath = path.join(defaultBasePath, 'bin', QUTS_PROCESS_NAME)
    return qutsPath
  }

  async function registerAndLaunch() {
    try {
      Win.appManager.register({
        'QPM': {
          path: findQpmPath(),
          onLaunch: function () {
            console.log('QPM was launched')
            try {
              setTimeout(() => {
                try {
                  // Win.appManager.switchTo('QPM')
                  setTimeout(() => tryLogin(onLoginDone), 2000)
                } catch (error) {
                  console.error(error)
                }
              }, 1000)
            } catch (error) {
              console.error(error)
            }
          },
        },
      })

      Win.appManager.launch('QPM')
    } catch (error) {
      console.error("win error: " + error)
    }
  }

  async function tryLogin(cb) {
    const loggedIn = await isLoggedIn()
    if (loggedIn) return cb(false)
    console.log('QPM is not logged in, trying to login now...')

    const user = config.QPM_USER
    const pass = config.QPM_PASSWORD
    if (!user || !pass) {
      throw new Error("QPM user and/or password not provided in config")
    }
    robot.typeString(user)
    robot.keyTap("tab")
    robot.typeString(pass)
    robot.keyTap("tab")
    robot.keyTap("enter")

    console.log('Login details filled')
    return cb(true)
  }

  function onLoginDone() {
    // Win.appManager.hide('QPM')
    console.log('>> QPM LAUNCH DONE <<')
    // launchQUTS()
  }

  async function launchQUTS() {
    const running = await isRunning('QUTS', QUTS_PROCESS_NAME)
    if (running) {
      console.log('QUTS service is running!')
    } else {
      console.log('QUTS service not running, starting it now...')
      const qutsPath = findQutsPath()
      const defaults = { cwd: path.parse(qutsPath).dir }
      exec(`runas /user:administrator "net start QUTS"`, defaults, function (err, stdout, stderr) {
        if (err) {
          console.error(err)
        } else {
          console.log("Started QUTS service:", stdout)
        }
      })
    }
  }

  // start here
  registerAndLaunch()

} catch (globalError) {
  console.error(globalError.message)
}