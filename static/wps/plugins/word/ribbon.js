
//这个函数在整个wps加载项中是第一个执行的
function OnAddinLoad(ribbonUI){
    if (typeof (wps.ribbonUI) != "object"){
		wps.ribbonUI = ribbonUI
    }
    
    if (typeof (wps.Enum) != "object") { // 如果没有内置枚举值
        wps.Enum = WPS_Enum
    }

    wps.PluginStorage.setItem("AiEnableFlag", true);
    wps.PluginStorage.setItem("EnableFlag", false) //往PluginStorage中设置一个标记，用于控制两个按钮的置灰
    wps.PluginStorage.setItem("ApiEventFlag", false) //往PluginStorage中设置一个标记，用于控制ApiEvent的按钮label
    return true
}

var WebNotifycount = 0;
function OnAction(control) {
    const eleId = control.Id
    switch (eleId) {
        case "about":
            {
                wps.ShowDialog("http://chat.testqa.cn/about", "关于", 400 * window.devicePixelRatio, 400 * window.devicePixelRatio, false)
            }
            break;
        case "aiChat":
            {
                wps.ShowDialog("http://chat.testqa.cn/", "Chatgpt对话", 1000 * window.devicePixelRatio, 600 * window.devicePixelRatio, false)
            }
            break;
        case "buy":
            {
                let tsId = wps.PluginStorage.getItem("bug_id")
                if (!tsId) {
                    let taskPanel = wps.CreateTaskPane("http://chat.testqa.cn/login")
                    taskPanel.Visible = true
                    wps.PluginStorage.setItem("bug_id", taskPanel.ID)
                } else {
                    let taskPanel = wps.GetTaskPane(tsId)
                    taskPanel.Visible = !taskPanel.Visible
                }
            }
            break;
        case "help":
            {
                let tsId = wps.PluginStorage.getItem("help_id")
                if (!tsId) {
                    let taskPanel = wps.CreateTaskPane(GetUrlPath() + "/ui/help.html")
                    taskPanel.Visible = true
                    wps.PluginStorage.setItem("help_id", taskPanel.ID)
                } else {
                    let taskPanel = wps.GetTaskPane(tsId)
                    taskPanel.Visible = !taskPanel.Visible
                }
            }
            break;
        case "aiAnswer":
            {
                let doc = wps.WpsApplication().ActiveDocument
                let data = {
                    status: '',
                    startTime: 0,
                    question: '',
                    answer: '等待回答'
                }
                if (doc){
                    // 获取选择的文本
                    let rgSel = wps.WpsApplication().Selection.Range;
                    if (rgSel && rgSel.Text.trim().length > 0) {
                        let question = rgSel.Text.trim();
                        // 设置请求信息
                        data.status = '请求已发送'
                        data.question = question
                        data.answer = '等待回答中，请耐心等待。如果请求失败会在此显示错误信息'
                        data.startTime = new Date().getTime();
                        wps.PluginStorage.setItem("request_info", data)
                        // 更新按钮状态
                        wps.PluginStorage.setItem("AiEnableFlag", false);
                        wps.ribbonUI.InvalidateControl("aiAnswer");
                        // 更新颜色
//                        let oldColor = rgSel.Style.Font.Color;
//                        var colorIndex = 0;
//                        const intervalId = setInterval(function() {
//                            rgSel.Style.Font.Color = [33333, oldColor][colorIndex / 2];
//                            colorIndex++;
//                        }, 1000);
                        // 发送请求
                        chatgpt_get(question, (answer) => {
                            console.log(answer);
                            // 设置响应信息
                            data.status = '请求已完成'
                            data.answer = answer;
                            data.endTime = new Date().getTime();
                            wps.PluginStorage.setItem("request_info", data)
                            debugger;
                            // 在被选择文本后追加回答内容
                            rgSel.InsertAfter("\n" + answer + "\n");
                            // 恢复按钮状态
                            wps.PluginStorage.setItem("AiEnableFlag", true);
                            wps.ribbonUI.InvalidateControl("aiAnswer");
                            // 恢复黑色
//                            rgSel.Style.Font.Color = oldColor;
//                            clearInterval(intervalId);
                        });
                    } else {
                        alert("请先选择需要提问的文本内容。")
                    }
                }
            }
            break;
        case "btnShowMsg":
            {
                const doc = wps.WpsApplication().ActiveDocument
                if (!doc) {
                    alert("当前没有打开任何文档")
                    return
                }
                alert(doc.Name)
            }
            break;
        case "btnIsEnbable":
            {
                let bFlag = wps.PluginStorage.getItem("EnableFlag")
                wps.PluginStorage.setItem("EnableFlag", !bFlag)
                
                //通知wps刷新以下几个按饰的状态
                wps.ribbonUI.InvalidateControl("btnIsEnbable")
                wps.ribbonUI.InvalidateControl("btnShowDialog") 
                wps.ribbonUI.InvalidateControl("btnShowTaskPane") 
                //wps.ribbonUI.Invalidate(); 这行代码打开则是刷新所有的按钮状态
                break
            }
        case "btnShowDialog":
            wps.ShowDialog(GetUrlPath() + "/ui/dialog.html", "这是一个对话框网页", 400 * window.devicePixelRatio, 400 * window.devicePixelRatio, false)
            break
        case "btnShowTaskPane":
            {
                let tsId = wps.PluginStorage.getItem("taskpane_id")
                if (!tsId) {
                    let tskpane = wps.CreateTaskPane(GetUrlPath() + "/ui/taskpane.html")
                    let id = tskpane.ID
                    wps.PluginStorage.setItem("taskpane_id", id)
                    tskpane.Visible = true
                } else {
                    let tskpane = wps.GetTaskPane(tsId)
                    tskpane.Visible = !tskpane.Visible
                }
            }
            break
        case "btnApiEvent":
            {
                let bFlag = wps.PluginStorage.getItem("ApiEventFlag")
                let bRegister = bFlag ? false : true
                wps.PluginStorage.setItem("ApiEventFlag", bRegister)
                if (bRegister){
                    wps.ApiEvent.AddApiEventListener('DocumentNew', OnNewDocumentApiEvent)
                }
                else{
                    wps.ApiEvent.RemoveApiEventListener('DocumentNew', OnNewDocumentApiEvent)
                }

                wps.ribbonUI.InvalidateControl("btnApiEvent") 
            }
            break
        case "btnWebNotify":
            {
                let currentTime = new Date()
                let timeStr = currentTime.getHours() + ':' + currentTime.getMinutes() + ":" + currentTime.getSeconds()
                wps.OAAssist.WebNotify("这行内容由wps加载项主动送达给业务系统，可以任意自定义, 比如时间值:" + timeStr + "，次数：" + (++WebNotifycount), true)
            }
            break
        default:
            break
    }
    return true
}

function GetImage(control) {
    const eleId = control.Id
    switch (eleId) {
        case "aiChat":
        case "aiAnswer":
            return "images/1.svg"
        case "btnShowMsg":
            return "images/1.svg"
        case "btnShowDialog":
            return "images/2.svg"
        case "btnShowTaskPane":
            return "images/3.svg"
        default:
            ;
    }
    return "images/newFromTemp.svg"
}

function OnGetEnabled(control) {
    const eleId = control.Id
    switch (eleId) {
        case "btnShowMsg":
            return true
            break
        case "aiAnswer":
            {
                let bFlag = wps.PluginStorage.getItem("AiEnableFlag")
                return bFlag ? true : false;
                break
            }
        case "btnShowDialog":
            {
                let bFlag = wps.PluginStorage.getItem("EnableFlag")
                return bFlag
                break
            }
        case "btnShowTaskPane":
            {
                let bFlag = wps.PluginStorage.getItem("EnableFlag")
                return bFlag
                break
            }
        default:
            break
    }
    return true
}

function OnGetVisible(control){
    const eleId = control.Id
    switch (eleId) {
        case "aiChat":
        case "aiEdit":
        case "aiImage":
        {
            return false
            break
        }
    }
    return true
}

function OnGetLabel(control){
    const eleId = control.Id
    switch (eleId) {
        case "btnIsEnbable":
        {
            let bFlag = wps.PluginStorage.getItem("EnableFlag")
            return bFlag ?  "按钮Disable" : "按钮Enable"
            break
        }
        case "btnApiEvent":
        {
            let bFlag = wps.PluginStorage.getItem("ApiEventFlag")
            return bFlag ? "清除新建文件事件" : "注册新建文件事件"
            break
        }    
    }
    return ""
}

function OnNewDocumentApiEvent(doc){
    alert("新建文件事件响应，取文件名: " + doc.Name)
}

function chatgpt_get(question, func) {
    const xmlReq = new XMLHttpRequest();
    var url = "http://chat.testqa.cn/api/chatgpt/answer?question=" + question;
    xmlReq.open("GET", url);
    xmlReq.onload = function (res) {
        if (xmlReq.status !== 200) {
            console.error('An error occurred: ' + xmlReq.status);
            alert("请求chatgpt失败，请联系插件管理人员");
        }
        let data = xmlReq.responseText;
        func(data);
    };
    xmlReq.send();
}
