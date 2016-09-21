
var Comment = React.createClass({
  rawMarkup: function() {
    var md = new Remarkable();
    var rawMarkup = md.render(this.props.children.toString());
    return { __html: rawMarkup };
  },

  render: function () {
    var formattedDate = new Date(this.props.posted)
    return (
      <div className="comment item">
        <div className="content">
          <div className="commentAuthor header">
            {this.props.author}
          </div>
          <div className="content">
            <div className="meta">
              <div className="date">
                {formattedDate.toUTCString()}
              </div>
            </div>
            <div className="description" dangerouslySetInnerHTML={this.rawMarkup()}>
            </div>
          </div>
        </div>
      </div>
    );
  }
});

var CommentList = React.createClass({
  render: function () {
    var commentNodes = this.props.data.map(function(comment) {
      return (
        <Comment
          author={comment.author}
          text={comment.text}
          posted={comment.posted}
          key={comment.posted}>
          {comment.text}
        </Comment>
      );
    });
    return (
      <div className="commentList ui relaxed divided items">
        {commentNodes}
      </div>
    );
  }
});

var CommentBox = React.createClass({
  loadCommentsFromServer: function () {
    return $.ajax({
      url: this.props.url,
      dataType: 'json',
      cache: false,
      success: function (data) {
        this.setState({data: data.comments});
      }.bind(this),
      error: function (xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  handleCommentSubmit: function (comment) {
    var comments = this.state.data;
    comment.id = Date.now();
    var newComments = comments.concat([comment]);
    this.setState({data: newComments});
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      type: 'POST',
      data: comment,
      success: function (data) {
        this.setState({data: data.comments});
      }.bind(this),
      error: function (xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  getInitialState: function () {
    return {data: []};
  },
  componentDidMount: function () {
    this.loadCommentsFromServer();
    setInterval(this.loadCommentsFromServer, this.props.pollInterval);
  },
  render: function () {
    return (
      <div className="commentBox">
        <CommentForm onCommentSubmit={this.handleCommentSubmit} />
        <CommentList data={this.state.data} />
      </div>
    );
  }
});

var CommentForm = React.createClass({
  getInitialState: function() {
    return {author: '', text: ''};
  },
  handleAuthorChange: function(e) {
    this.setState({author: e.target.value});
  },
  handleTextChange: function(e) {
    this.setState({text: e.target.value});
  },
  handleSubmit: function (e) {
    e.preventDefault();
    var author = this.state.author.trim();
    var text = this.state.text.trim();
    if (!text || !author ) {
      return;
    }
    this.props.onCommentSubmit({author: author, text: text, posted: new Date()});
    this.setState({author: '', text: ''});
    return;
  },
  render: function () {
    return (
      <div className="ui segment">
      <form className="commentForm ui form" onSubmit={this.handleSubmit}>
        <div className="field">
          <label>Your Name</label>
          <input
            type="text"
            placeholder="Your name"
            value={this.state.author}
            onChange={this.handleAuthorChange}
          />
        </div>
        <div className="field">
          <label>Comment</label>
          <textarea
            type="textarea"
            placeholder="Say something..."
            value={this.state.text}
            onChange={this.handleTextChange}
          />
        </div>
        <button className="ui button blue" type="submit" value="Post">Submit</button>
      </form>
      </div>
    );
  }
});

ReactDOM.render(
  <CommentBox url="/comments" pollInterval={5000} />,
  document.getElementById('content')
);
