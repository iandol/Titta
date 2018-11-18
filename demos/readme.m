sca
qDEBUG = 0;
s.bclr              = 255/2;

addpath(genpath(fullfile(cd,'..')));

try
    % get setup struct (can edit that of course):
    settings = Titta.getDefaults('Tobii Pro Spectrum');
    settings.cal.autoPace = 0;
    settings.setup.startScreen = 1;
%     settings.cal.pointPos           = [[0.25 0.75]; [0.75 0.25]];
%     settings.val.pointPos           = [[0.25 0.25]; [0.75 0.75]];
    % custom calibration drawer
    calViz = AnimatedCalibrationDisplay();
    settings.cal.drawFunction = @calViz.doDraw;
    settings.debugMode = true;
    
    % init
    ETFhndl         = Titta(settings);
%     ETFhndl         = ETFhndl.setDummyMode();
    ETFhndl.init();
    
    
    if qDEBUG>1
        % make screen partially transparent on OSX and windows vista or
        % higher, so we can debug.
        PsychDebugWindowConfiguration;
    end
    if qDEBUG
        % Be pretty verbose abDout information and hints to optimize your code and system.
        Screen('Preference', 'Verbosity', 4);
    else
        % Only output critical errors and warnings.
        Screen('Preference', 'Verbosity', 2);
    end
    Screen('Preference', 'SyncTestSettings', 0.002);    % the systems are a little noisy, give the test a little more leeway
    wpnt = PsychImaging('OpenWindow', 0, s.bclr);
    Priority(1);
    Screen('BlendFunction', wpnt, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    Screen('Preference', 'TextAlphaBlending', 1);
    Screen('Preference', 'TextAntiAliasing', 2);
    % This preference setting selects the high quality text renderer on
    % each operating system: It is not really needed, as the high quality
    % renderer is the default on all operating systems, so this is more of
    % a "better safe than sorry" setting.
    Screen('Preference', 'TextRenderer', 1);
    KbName('UnifyKeyNames')
    
    % do calibration
    tobii.calVal{1}   = ETFhndl.calibrate(wpnt);
    
    % later:
    ETFhndl.startRecording('gaze');
     
    % send message into ET data file
    ETFhndl.sendMessage('test');
    % record 2 seconds of data
    WaitSecs(2);
    
    ETFhndl.startRecording('eyeImage');
    ETFhndl.sendMessage('eyes!');
    WaitSecs(.8);
    
    
    
    % stopping and saving
    ETFhndl.stopRecording('eyeImage');
    ETFhndl.stopRecording('gaze');
    ETFhndl.saveData(fullfile(cd,'t'), true);
    
    % shut down
    ETFhndl.deInit();
catch me
    sca
    rethrow(me)
end
sca