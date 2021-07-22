var grunt = require('grunt')

exports['tar'] = {
	setUp: function (done) {
		done()
	},

	'helper': function (test) {
		test.expect(1)
		test.equal(1, 1, 'the world should be sane.')
		test.done()
	}
}
