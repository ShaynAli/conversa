function varargout = cnv_eval(predictor, labels, algoNames, varargin)
% Evaluates learning algorithms
% By Shayaan Syed Ali
% Last updated 19-Jun-17

% SET PARAMETERS ==========================================================
% Process varargin to apply input arguments as needed

% Initialize optional arguments default values
% Format is struct('fieldName1', 'defaultValue1', 'fieldName2', 'defaultValue2', ...)
optionArgs = struct( ... % TODO: Setup optionArgs with default vals and then set via getArgs
	'trainsize', '0.8' ... % Testing with 80% of the data by default, giving 20% of the data for testing
	    );
optionArgs = cnv_getArgs(optionArgs, varargin); % Get and set args as provided
% TODO: Check optionArgs for error (e.g. trainsize <= 0 or trainsize > 1)

% Set basic info about the data
nSamples = size(predictor, 1);
if (nSamples ~= size(labels, 1)) % Labels and predictors must have corresponding rows
	error('The number of rows in the predictor matrix and label mamtrix are not equal');
end;
nTrainSamples = round(nSamples*(optionArgs.trainsize)); % Number of rows, since 
nTestSamples = nSamples - nTrainSamples; % All non-training samples are for testing
nPartitions = ceil(1/optionArgs.trainsize);

% PARTITION DATA ==========================================================
% Partition data into learning and testing sets for training and evaluation

testStartI = zeros(nPartitions, 1);
testEndI = zeros(nPartitions, 1);
% Set test partition indices except last partition
for i = 1:(nPartitions-1)
	testStartI(i) = (i-1)*nTestSamples;
	testEndI(i) = (i)*nTestSamples;
end;
% Set last partition
testStartI(nPartitions) = nSamples - nTestSamples;
testEndI(nPartitions) = nSamples;

% TRAIN AND TEST ==========================================================
% Train and test algorithms, returning an error rate

% Set lists of learning and prediction functions from the algoNames
learnPrefix = 'cnv_learn_';
predictionPrefix = 'cnv_predict_';
learnFunctions = preSufFuncList({learnPrefix}, algoNames)';
predictFunctions = preSufFuncList({predictionPrefix}, algoNames)';

% Train from 1 to testStartI-1 and testEndI+1 to nSamples
% Test from testStartI to testEndI
% (All bounds inclusive)

end

% Returns a function handle for the function with the name prefix ||
% suffix, i.e. the prefix and suffix concatenated as in @prefixsuffix
function out = preSufFunc(prefix, suffix)
out = str2func(strcat(prefix, suffix));
end

% Returns function handle list with all combos from the prefixList and
% suffixList
function out = preSufFuncList(prefixes, suffixes)
nPrefixes = length(prefixes);
nSuffixes = length(suffixes);
out = cell(nPrefixes, nSuffixes);
for i = 1:nPrefixes
    for j = 1:nSuffixes
        out{i, j} = preSufFunc(prefixes{i}, suffixes{j});
    end;
end;
end